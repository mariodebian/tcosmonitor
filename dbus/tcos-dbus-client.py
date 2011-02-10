#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#    TcosMonitor version __VERSION__
#
# Copyright (c) 2006-2011 Mario Izquierdo <mariodebian@gmail.com>
#
# This package is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
#
# This package is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os, sys
import getopt

#if os.path.isdir('./debian') and os.path.isdir('./po'):
#    sys.path.insert(0, './')

from tcosmonitor import shared


print "tcos-dbus-client: starting daemon..."


#shared.debug=True
def print_debug(txt):
    if shared.debug:
        print "%s::%s" %("TcosDBusServer()", txt)


try:
    opts, args = getopt.getopt(sys.argv[1:], ":hd", ["help", "debug", "only-local"])
except getopt.error, msg:
    print msg
    print "for command line options use tcos-dbus-client --help"
    sys.exit(2)



for o, a in opts:
    if o in ("-d", "--debug"):
        print "DEBUG ACTIVE"
        shared.debug = True
    if o == "--only-local":
        shared.allow_local_display=True


host =  str(shared.parseIPAddress(os.environ["DISPLAY"]))
if host == "" and not shared.allow_local_display:
	print "tcos-dbus-client: Not allowed to run in local DISPLAY"
	sys.exit(0)
	
if host != "" and shared.allow_local_display:
	print "tcos-dbus-client: Not allowed to run in remote DISPLAY: \"%s\"" %(host)
	sys.exit(0)
	
from tcosmonitor.TcosDBus import TcosDBusServer
try:
    server=TcosDBusServer().start()
except KeyboardInterrupt:
    print_debug("Ctrl+C exiting...")
    sys.exit(0)


