#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
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
from gettext import gettext as _



if os.geteuid() != 0:
    print "tcos-server-utils ERROR: you must be root to run this"
    sys.exit(1)

# append current dir to sys-path if exec from sources
for m in range(len(sys.path)):
    if "server-utils" in sys.path[m]:
        sys.path[m]=os.path.dirname(sys.path[m])

from tcosmonitor import shared


def print_debug(txt):
    if shared.debug:
        print "%s::%s" %("tcos-server-utils", txt)



shared.from_cron=False
actions=["reboot", "poweroff", "restartx", "message", "nothing"]
action = ""
text=""
users=""

def usage():
    print "tcos-server-utils help:"
    print ""
    print "   tcos-server-utils --action=XXX  (action must be: %s ) "                %(", ".join(actions) )
    print "                                   (use --action=nothing to test with doing nothing!!!)" 
    print "   tcos-server-utils --text=\"foo\" (if action=message this text will be displayed "
    print "                                     in all connected users with notification-daemon)"
    print "                     --users=foo,bar (coma separated list of users we want to do action"
    print "                                      only valid for --action=message)"
    print "   tcos-server-utils -d [--debug]  (write debug data to stdout)"
    print "   tcos-server-utils -h [--help]   (this help)"


try:
    opts, args = getopt.getopt(sys.argv[1:], ":hd", ["help", "cron", "debug", "action=", "text=", "users="])
except getopt.error, msg:
    print msg
    print "for command line options use tcos-server-utils --help"
    sys.exit(2)



# process options
for o, a in opts:
    if o in ("--help"):
        usage()
        sys.exit(0)
        
    if o in ("-d", "--debug"):
        shared.debug = True
    if o in ("--cron"):
        shared.from_cron=True
    if o == "--action":
        if not a in actions:
            print "TCOS tcos-server-utils ERROR: action \"%s\" not avalaible" %(a)
            sys.exit(1)
        action = a
    if o == "--text":
        text=a
    if o == "--users":
        users=a


if action=="":
    print "tcos-server-utils ERROR: action must be in: %s" %(", ".join(actions) )
    sys.exit(0)


class ServerUtils:
    def __init__(self):
        self.name="ServerUtils"
        self.worker_running = False
        
        # get all devices
        import tcosmonitor.TcosCommon
        import tcosmonitor.TcosXmlRpc
        import tcosmonitor.TcosConf
        self.common=tcosmonitor.TcosCommon.TcosCommon(self)
        self.config=tcosmonitor.TcosConf.TcosConf(self)
        self.xmlrpc=tcosmonitor.TcosXmlRpc.TcosXmlRpc(self)
        
        
        if self.config.GetVar("xmlrpc_username") == "" or self.config.GetVar("xmlrpc_password") == "":
            print "tcos-server-utils ERROR: need to create /root/.tcosmonitor.conf with user and pass."
            print "                         see /usr/share/doc/tcosmonitor/README.tcos-server-utils"
            sys.exit(1)
        
        import tcosmonitor.LocalData
        self.localdata=tcosmonitor.LocalData.LocalData(self)
        
        self.alltcosclients=[]
        self.allclients=self.localdata.GetAllClients("netstat")
        
        if len(self.allclients) == 0:
            print "tcos-server-utils No host connected, exiting..."
            sys.exit(0)
        
        for host in self.allclients:
            self.xmlrpc.newhost(host)
            if self.xmlrpc.connected:
                print_debug ("Host %s connected" %(host) )
                self.alltcosclients.append(host)
            else:
                print_debug ("Host %s NOT connected" %(host) )
        
        
        print ("Doing action \"%s\" in %s" %(action, self.alltcosclients) )
        
        if action == "message":
            if text != "":
                print ( "Searching for all connected users..." )
                
                connected_users=[]
                #connected_users=['magna26']
                if users != "":
                    connected_users = users.split(',')
                    print "Users from cdmline: %s" %(connected_users)
                else:
                    
                    for client in self.alltcosclients:
                        if self.localdata.IsLogged(client):
                            connected_users.append(self.localdata.GetUsername(client))
                
                    print ( "Connected users: %s" %connected_users)
                        
                from tcosmonitor.TcosDBus import TcosDBusAction
                self.dbus_action=TcosDBusAction( self, \
                    admin=self.config.GetVar("xmlrpc_username"), \
                    passwd=self.config.GetVar("xmlrpc_password") )
                
                result=self.dbus_action.do_message ( connected_users, text )
                if not result:
                    print "ERROR: sending dbus msg: %s" %(self.dbus_action.get_error_msg() )
                else:
                    print "DBus message send ok."
                    
            else:
                print ( "ERROR: message action need a --text value" )
        
        
        for client in self.alltcosclients:
            if action == "reboot":
                print ( "Restarting %s..."  %client )
                self.xmlrpc.newhost(client)
                self.xmlrpc.Exe("reboot")
            elif action == "poweroff":
                print ( "Shutting down %s..."  %client )
                self.xmlrpc.newhost(client)
                self.xmlrpc.Exe("poweroff")
            elif action == "restartx":
                print ( "Restarting Xorg of %s..."  %client )
                self.xmlrpc.newhost(client)
                self.xmlrpc.Exe("restartx")
            elif action == "message":
                pass
            else:
                print ( "Unknow action %s in client %s" %(action, client) )
                


if __name__ == "__main__":
    app=ServerUtils()

