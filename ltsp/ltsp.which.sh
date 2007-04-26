#!/bin/sh

_app=$1

_PATH="/bin /usr/bin /sbin /usr/sbin /usr/local/bin /usr/local/sbin"
for _path in $_PATH; do

  if [ -f $_path/$_app ]; then
     echo $_path/$_app
     exit 0
  fi

done

echo $_appt not found in path
exit 1

