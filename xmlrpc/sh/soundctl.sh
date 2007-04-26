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


# aumix commands
# 
# aumix -q print all channels info
# aumix -v 80% (set master to 90%)

CMD="amixer -c 0 "

output=""
need_parse="0"
unmute_level="80"

if [ -e /dev/dsp ] && [ ! -d /proc/asound ]; then
  TCOS_OSS=1
  MIXER="aumix"
else
  TCOS_OSS=
  MIXER="amixer -c 0 "
fi

# for debug force OSS
TCOS_OSS=1
MIXER="aumix"
#####################

get_controls() {
  if [ $TCOS_OSS ]; then
    $MIXER -q | awk '{print $1}'
  else
    $MIXER scontrols | awk -F " control " '{print $2}'| awk -F "," '{print $1}' | sed s/"'"//g
  fi
}

get_level() {
  if [ "$1" = "" ]; then
   echo "soundctl error, need a control to retrieve data"
   exit 1
  fi
  
  if [ $TCOS_OSS ]; then
    $MIXER -q | grep $1 | head -1 | awk '{print $3}' | sed s/","//g
  else
    $MIXER  sget "$1" | grep "^  Front"| head -1 | awk '{print $5}'| sed s/"\["//g| sed s/"\]"//g
  fi
}

set_level() {
 if [ "$1" = "" ]; then
   echo "soundctl error, need a control to retrieve data"
   exit 1
 fi
 if [ "$2" = "" ]; then
   echo "soundctl error, need a xxx% level or 1-31 int"
   exit 1
 fi
 
 if [ $TCOS_OSS ]; then
    if [ "$1" = "vol" ]; then
      $MIXER -v "$2" ; get_level "$1"
    elif [ "$1" = "pcm" ]; then
      $MIXER -w "$2" ; get_level "$1"
    elif [ "$1" = "line" ]; then
      $MIXER -l "$2" ; get_level "$1"
    elif [ "$1" = "mic" ]; then
      $MIXER -m "$2" ; get_level "$1"
    elif [ "$1" = "cd" ]; then
      $MIXER -c "$2" ; get_level "$1"
    else
      echo "unknow OSS mixer channel"
    fi
 else
    $MIXER  set "$1" "$2" | grep "^  Front"| head -1 | awk '{print $5}'| sed s/"\["//g| sed s/"\]"//g
 fi
}

get_mute() {
 if [ "$1" = "" ]; then
   echo "soundctl error, need a control to retrieve data"
   exit 1
 fi
 if [ $TCOS_OSS ]; then
    if [ "$(get_level $1)" = "0" ]; then
      echo "off"
    else
      echo "on"
    fi
  else
    $MIXER  sget $1| grep "^  Front"| head -1 | awk '{print $6}'| sed s/"\["//g| sed s/"\]"//g
  fi
}

set_mute() {
 if [ "$1" = "" ]; then
   echo "soundctl error, need a control to retrieve data"
   exit 1
 fi
 if [ $TCOS_OSS ]; then
    set_level "$1" "0"
  else
    $MIXER  set $2 mute| grep "^  Front"| head -1 | awk '{print $6}'| sed s/"\["//g| sed s/"\]"//g
  fi
}

set_unmute() {
 if [ "$1" = "" ]; then
   echo "soundctl error, need a control to retrieve data"
   exit 1
 fi
 if [ $TCOS_OSS ]; then
    set_level "$1" "$unmute_level"
  else
    $MIXER set $2 unmute| grep "^  Front"| head -1 | awk '{print $6}'| sed s/"\["//g| sed s/"\]"//g
  fi
}

read_line() {
head -$1 /tmp/soundctl | tail -1
}

if [ "$1" = "--showcontrols" ]; then
 output=$(get_controls)
 need_parse="1"
fi

if [ "$1" = "--getlevel" ]; then
 output=$(get_level "$2")
fi


if [ "$1" = "--setlevel" ]; then
 output=$(set_level "$2" "$3")
fi

if [ "$1" = "--getmute" ]; then
 output=$(get_mute "$2")
fi

if [ "$1" = "--setmute" ]; then
 output=$(set_mute "$2")
fi

if [ "$1" = "--setunmute" ]; then
 output=$(set_unmute "$2")
fi


if [ "$1" = "--getserverinfo" ]; then
  if [ "$(pidof pulseaudio)" = "" ]; then
    echo "error: pulseaudio not running"
    exit 1
  fi
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
