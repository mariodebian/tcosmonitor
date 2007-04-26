#!/bin/sh
# Sound volume control

# amixer commands:
#
#Available options:
#  -h,--help       this help
#  -c,--card N     select the card
#  -D,--device N   select the device, default 'default'
#  -d,--debug      debug mode
#  -n,--nocheck    do not perform range checking
#  -v,--version    print version of this program
#  -q,--quiet      be quiet
#  -i,--inactive   show also inactive controls
#  -a,--abstract L select abstraction level (none or basic)
#  -s,--stdin      Read and execute commands from stdin sequentially
#
#Available commands:
#  scontrols       show all mixer simple controls
#  scontents       show contents of all mixer simple controls (default command)
#  sset sID P      set contents for one mixer simple control
#  sget sID        get contents for one mixer simple control
#  controls        show all controls for given card
#  contents        show contents of all controls for given card
#  cset cID P      set control contents for one control
#  cget cID        get control contents for one control


read_line() {
head -$1 /tmp/soundctl | tail -1
}

CMD="amixer -c 0 "

output=""
need_parse="0"


if [ "$1" = "--showcontrols" ]; then
 output=$($CMD  scontrols| awk -F " control " '{print $2}'| awk -F "," '{print $1}' | sed s/"'"//g)
 need_parse="1"
fi

if [ "$1" = "--getlevel" ]; then
 if [ "$2" = "" ]; then
   echo "soundctl error, need a control to retrieve data"
   exit 1
 fi
 output=$($CMD  sget "$2" | grep "^  Front"| head -1 | awk '{print $5}'| sed s/"\["//g| sed s/"\]"//g)
fi

if [ "$1" = "--setlevel" ]; then
 if [ "$2" = "" ]; then
   echo "soundctl error, need a control to retrieve data"
   exit 1
 fi
 if [ "$3" = "" ]; then
   echo "soundctl error, need a xxx% level or 1-31 int"
   exit 1
 fi
 output=$($CMD  set "$2" "$3" | grep "^  Front"| head -1 | awk '{print $5}'| sed s/"\["//g| sed s/"\]"//g)
fi

if [ "$1" = "--getmute" ]; then
 if [ "$2" = "" ]; then
   echo "soundctl error, need a control to retrieve data"
   exit 1
 fi
 output=$($CMD  sget $2| grep "^  Front"| head -1 | awk '{print $6}'| sed s/"\["//g| sed s/"\]"//g)
fi


if [ "$1" = "--setmute" ]; then
 if [ "$2" = "" ]; then
   echo "soundctl error, need a control to retrieve data"
   exit 1
 fi
 output=$($CMD  set $2 mute| grep "^  Front"| head -1 | awk '{print $6}'| sed s/"\["//g| sed s/"\]"//g)
fi

if [ "$1" = "--setunmute" ]; then
 if [ "$2" = "" ]; then
   echo "soundctl error, need a control to retrieve data"
   exit 1
 fi
 output=$($CMD  set $2 unmute| grep "^  Front"| head -1 | awk '{print $6}'| sed s/"\["//g| sed s/"\]"//g)
fi

if [ "$1" = "--getserverinfo" ]; then
  pactl -s 127.0.0.1 stat > /tmp/soundinfo
  output=$(cat /tmp/soundinfo)
  rm /tmp/soundinfo
  need_parse=1
fi

usage() {
  echo "Usage:"
  echo "       $0  --help                  ( this help text )"
  echo "       $0  --showcontrols          ( return all mixer channels )"
  echo "       $0  --getlevel CHANNEL      ( return CHANNEL level xx% xx% left and right )"
  echo "       $0  --setlevel CHANNEL xx%  ( change and return CHANNEL level xx% xx% left and right )"
  echo "       $0  --getmute CHANNEL       ( return off if mute or on if unmute CHANNEL )"
  echo "       $0  --setmute CHANNEL       ( mute CHANNEL and return off if succesfull )"
  echo "       $0  --setunmute CHANNEL     ( unmute CHANNEL and return on if succesfull )"
  echo "       $0  --getserverinfo         ( show stats of PulseAudio server with pactl)"
}


if [ "$1" = "" -o "$1" = "--help" ]; then
  usage
  exit 1
fi

if [ "$output" = "" ]; then
  output="unknow"
fi

if [ "$need_parse" = "1" ]; then
  echo "$output" > /tmp/soundctl
  num_lines=$(cat /tmp/soundctl | wc -l)
  for i in $(seq 1 $num_lines); do
    line=$(read_line $i)
    echo -n "$line|"
  done
  rm /tmp/soundctl
else
  echo -n $output
fi

exit 0
