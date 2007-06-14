#!/bin/sh
# Devices remote control

tmp_file=/tmp/devicesctl

output=""
need_parse="0"

LANG=C
FDISK="/sbin/fdisk"

read_line() {
  head -$1 $tmp_file | tail -1
}

get_fs_type() {
    type=$($FDISK -l /dev/$1 |grep ^/dev | awk '{if ($2 == "*") {print $6};}{if ($2 != "*") {print $5};}')
    case "$type" in
      83)
       output="ext3"
       ;;
      82)
       output="swap"
       ;;
      b)
       output="vfat"
       ;;
      c)
       output="vfat"
       ;;
      e)
       output="vfat"
       ;;
      f)
       output="extended"
       ;;
      7)
       output="ntfs"
       ;;

      *)
       output="unknow"
       ;;
  esac
  echo $output
}




if [ "$1" = "--showlocaldisks" ]; then
 #output=$($FDISK -l | awk '/^\/dev/ {print $1}')
 output=$(ls /sys/block/|grep -v ram|grep -v loop)
 need_parse="1"
fi

if [ "$1" = "--getsize" ]; then
  if [ "$2" != "" ]; then
    output=$($FDISK -l /dev/$2 | grep "/dev/$2:" | awk  '{print $3" "$4}' | sed s/,//g)
  else
    output="error: need a device!!"
  fi
fi


if [ "$1" = "--getparts" ]; then
  if [ "$2" != "" ]; then
    allparts=$(echo /sys/block/$2/$2*)
    for part in $allparts; do echo $(basename $part) >> $tmp_file ;done
    need_parse=1
    output="tmp_file"
  else
    output="error: need a device!!"
  fi
fi

if [ "$1" = "--gettype" ]; then
  if [ "$2" != "" ]; then
    output=$(get_fs_type $1)
  else
    output="error: need a device!!"
  fi
fi

if [ "$1" = "--getdmesg" ]; then
  output=$(dmesg|tail)
  need_parse=1
fi


if [ "$1" = "--getudev" ]; then
  output=$(cat /tmp/tcos-udevd.log 2>/dev/null)
  cat /dev/null > /tmp/tcos-udevd.log
  need_parse=1
fi


if [ "$1" = "--mount" ]; then
  if [ "$2" != "" ]; then
      mnt=$(basename $2)
      fs=""
      if [ "$3" != "" ]; then
         fs=" -t $3 "
      fi
      mkdir -p /mnt/$mnt
      mount $2 $fs /mnt/$mnt 2>/dev/null
      if [ $? = 0 ]; then
        output="/mnt/$mnt"
      else
        output="error: mounting device"
      fi
  else
      output="error: need a device"
  fi
fi


if [ "$1" = "--umount" ]; then
  if [ "$2" != "" ]; then
    mnt=$(basename $2)
    umount /mnt/$mnt
    if [ $? = 0 ]; then
      output="/mnt/$mnt"
    else
      output="error: umounting device"
    fi
  else
    output=$"error: need something to umount"
  fi
fi


if [ "$1" = "--getstatus" ]; then
 if [ "$2" != "" ]; then
   output=$(grep -c ^$2 /proc/mounts)
 else
   output="error: need a device"
 fi

fi

if [ "$1" = "--eject" ]; then
 if [ "$2" != "" ]; then
   eject /dev/$2
 else
   eject
 fi
 echo "ok"

fi


if [ "$1" = "--getcdrom" ]; then
  cdrom=$(head -3 /proc/sys/dev/cdrom/info 2>/dev/null | tail -1 | cut -f 3-)
  for item in $cdrom; do output="$output$item|"; done
  need_parse=0
fi


if [ "$1" = "--getxdrivers" ]; then
  if [ -d /usr/lib/xorg/modules/drivers/ ]; then
    output=$(ls /usr/lib/xorg/modules/drivers/|grep "_drv.so"|sed s/'_drv.so'//g)
  fi
  need_parse=1
fi

if [ "$1" = "--exists" ]; then
  if [ -e "$2" ]; then
    output=1
  else
    output=0
  fi
  need_parse=0
fi



usage() {
  echo "Usage:"
  echo "       $0  --help                  ( this help text )"
  echo "       $0  --showlocaldisks        ( return all devices )"
  echo "       $0  --getsize  DEVICE       ( return size of DEVICE )"
  echo "       $0  --getparts DEVICE       ( return partittions of DEVICE )"
  echo "       $0  --getdmesg              ( return last lines of dmesg )"
  echo "       $0  --getcdrom              ( return all cdrom devices )"
  echo "       $0  --getxdrivers           ( return all xorg drivers found )"
}


if [ "$1" = "" -o "$1" = "--help" ]; then
  usage
  exit 1
fi

if [ "$output" = "" ]; then
  output="unknow"
fi

if [ "$need_parse" = "1" ]; then
  if [ "$output" != "tmp_file" ]; then
    echo "$output" > $tmp_file
  fi
  num_lines=$(cat $tmp_file | wc -l)
  for i in $(seq 1 $num_lines); do
    line=$(read_line $i)
    echo -n "$line|"
  done
  rm $tmp_file
else
  echo -n $output
fi

exit 0
