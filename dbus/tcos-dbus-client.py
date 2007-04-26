#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os, sys

host, display =  os.environ["DISPLAY"].split(':')
if host == "":
	print "tcos-dbus-client: Not allowed to run in local DISPLAY"
	sys.exit(0)


if not os.path.isfile("shared.py"):
	#print "tcos-dbus-client: adding path..."
	sys.path.append('/usr/share/tcosmonitor')
else:
	sys.path.append('./')
	

print "tcos-dbus-client: starting daemon..."

import shared
#shared.debug=True
def print_debug(txt):
    if shared.debug:
        print "%s::%s" %("TcosDBusServer()", txt)

# check for pulseaudio server and export vars
# FIXME FIXME
#from ping import PingPort
#if PingPort(host, 4713, 0.5).get_status() == "OPEN":
#    # we have pulseaudio running, export some vars...
#    print "exporting vars..."
#    os.putenv("PULSE_SERVER", host )



from TcosDBus import TcosDBusServer
server=TcosDBusServer().start()
