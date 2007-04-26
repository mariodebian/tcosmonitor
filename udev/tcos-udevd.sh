#!/bin/sh
# tcos-udev.sh
# exec by udevd in some events

output_file=/tmp/tcos-udevd.log

get_env_var() {
  env_var=$(env |grep ^$1=)
  echo $env_var
}

udev_date=$(date +%Y-%m-%d_%H:%M:%S)
   id_bus=$(get_env_var "ID_BUS")
   device=$(get_env_var "DEVNAME")
   action=$(get_env_var "ACTION")
    label=$(get_env_var "ID_FS_LABEL")
  fs_type=$(get_env_var "ID_FS_TYPE")
   vendor=$(get_env_var "ID_VENDOR")
    model=$(get_env_var "ID_MODEL")
   
echo "$udev_date#$id_bus#$device#$action#$label#$fs_type#$vendor#$model" >> $output_file
