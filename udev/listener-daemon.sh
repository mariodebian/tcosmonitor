#!/bin/sh

#
# Launch listener_mounter (see if /proc/mounts changes)
# and generate a udev mount/umount event
# only needed with kernel => 2.6.22
# 3106d46f51a1a72fdbf071ebc0800a9bcfcbc544
# patch-2.6.21-git3.log
#

# exit if kernel < 2.6.22
KMAY=$(uname -r | awk -F"." '{print $1}')
KMED=$(uname -r | awk -F"." '{print $2}')
KMIN=$(uname -r | awk -F"." '{print $3}' | awk -F"-" '{print $1}')

if [ $KMIN -lt 22 ]; then
  exit 0
fi

MOUNT_LISTENER=/sbin/mount_listener
enable_debug=1
output_file=/tmp/tcos-udevd.log
MOUNTS=/proc/mounts
LAST_MOUNTS=/tmp/proc_mounts

restore(){
  cat $MOUNTS > $LAST_MOUNTS
}

debug() {
 [ "$enable_debug" = 1 ] && echo "   *** DEBUG: $@" >&2
}

diff_lines() {
echo "$1 $2"|awk '{print $1-$2}'
}


do_action() {
  #/dev/hda3 /home ext3 rw,data=ordered 0 0
  DEVNAME=$1
  MNT=$2
  ACTION=$7
  debug "DEVNAME=$DEVNAME MNT=$MNT ACTION=$ACTION"
  # DEVNAME is something like ^/dev ??
  if [ "$(echo $DEVNAME| awk -F "/" '{print $2}')" != "dev" ]; then
   debug "$DEVNAME is not /dev"
   return
  fi
  if [ "$(echo $DEVNAME| awk -F "/" '{print $3}'| cut -c2)" != "d" ]; then
   debug "$DEVNAME is not /dev/?d*"
   return
  fi

  PART=$(echo "/dev/sda1" | awk -F"/" '{print $3}')
  DISK=$(echo "$PART" | cut -c-3)
  DEVPATH="/block/$DISK"
  [ "$PART" != "$DISK" ] && DEVPATH="/block/$DISK/$PART"

  export $(udevinfo --path=/sys$DEVPATH --query=env )
  echo "ID_BUS=$ID_BUS#DEVNAME=$DEVNAME#ACTION=$ACTION#ID_FS_LABEL=$ID_FS_LABEL#ID_FS_TYPE=$ID_FS_TYPE#ID_VENDOR=$ID_VENDOR#ID_MODEL=$ID_MODEL#DEVPATH=$DEVPATH" >> $output_file
  debug "ID_BUS=$ID_BUS#DEVNAME=$DEVNAME#ACTION=$ACTION#ID_FS_LABEL=$ID_FS_LABEL#ID_FS_TYPE=$ID_FS_TYPE#ID_VENDOR=$ID_VENDOR#ID_MODEL=$ID_MODEL#DEVPATH=$DEVPATH"
}



launch_action() {
 mounts=$(cat $MOUNTS |wc -l)
 old=$(cat $LAST_MOUNTS | wc -l)
 if [ "$mounts" -gt "$old" ]; then
  debug "detected mount device"
  for i in $(seq $(diff_lines $mounts $old)); do
   do_action $(cat $MOUNTS | tail -$i | head -1) mount
  done
 else
  debug "detected umount device"
  for i in $(seq $(diff_lines $old $mounts)); do
   do_action $(cat $LAST_MOUNTS | tail -$i  | head -1) umount
  done
 fi
 restore
}

if [ ! -x $MOUNT_LISTENER ]; then
   echo "$MOUNT_LISTENER not found"
   exit 1
fi

######### start loop #############

restore
while [ 1 ]; do
 $MOUNT_LISTENER && launch_action
done
