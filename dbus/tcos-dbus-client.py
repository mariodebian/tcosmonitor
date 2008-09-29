#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##########################################################################
# TcosMonitor writen by MarioDebian <mariodebian@gmail.com>
#
#    tcos-devices-ng version __VERSION__
#
# Copyright (c) 2006 Mario Izquierdo <mariodebian@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
###########################################################################

import os, sys
import getopt

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


host, display =  os.environ["DISPLAY"].split(':')
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


