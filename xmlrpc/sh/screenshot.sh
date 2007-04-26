#!/bin/sh

# screenshot.sh shell script to make and screenshot with scrot
#               and save it in /var/www
#  2006-09-09 14:22:40 mariodebian $
#
# This file is part of tcosxmlrpc.
#
# tcosxmlrpc is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# tcosxmlrpc is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with tcosxmlrpc; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA.

_www=/var/www
_tmp=/tmp/screenshot
_port=8081
_thumb_size=65

if [ "$1" != "" ]; then
  _thumb_size=$1
fi

export DISPLAY=:0

rm -rf $_tmp
mkdir $_tmp
cd $_tmp

scrot 'capture.png' -t $_thumb_size

mkdir -p $_www


# start httpd in init scripts !!!!
#httpd_running=$(ps aux|grep httpd|grep -v grep | wc -l)
#if [ $httpd_running -lt 1 ]; then
#  starthttpd
#fi

mv *png $_www

cd /
rm -rf $_tmp

cd /var/www
_files=$(ls *png)

cat << EOF > /var/www/index.html
<html>
<head>
<title>Screenshots</title>
</head>
<body>
<H1>Screenshots of $(hostname),<br>take on $(date)</H1>
<br><br>
EOF
for _file in $_files; do
 #echo "<a href=\"$_file\">  <img src=\"$_file\">  </a><br>" >> /var/www/index.html
 echo "<a href=\"$_file\">$_file</a><br>" >> /var/www/index.html
done

cat << EOF >> /var/www/index.html
</body>
</html>
EOF

