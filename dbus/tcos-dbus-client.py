#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os, sys
import getopt




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
	



from TcosDBus import TcosDBusServer
try:
    server=TcosDBusServer().start()
except KeyboardInterrupt:
    print_debug("Ctrl+C exiting...")
    sys.exit(0)
