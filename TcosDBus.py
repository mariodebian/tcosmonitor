# -*- coding: UTF-8 -*-
##########################################################################
# TcosMonitor writen by MarioDebian <mariodebian@gmail.com>
#
#    TcosMonitor version __VERSION__
#
# Copyright (c) 2006 Mario Izquierdo <mariodebian@gmail.com>
# All rights reserved.
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

# dbus classes for tcosmonitor

import dbus
import dbus.service
import dbus.glib
import gobject
import os
import signal
import subprocess
import pwd
import sys
from gettext import gettext as _


import shared
def print_debug(txt):
    if shared.debug:
        print "%s::%s" %(__name__, txt)


class TcosDBusServer:
    def __init__(self):
        self.username = pwd.getpwuid(os.getuid())[0]
        self.admin=None
        self.passwd=None
        self.error_msg=None
        print_debug ( "TcosDBusServer() __init__ as username=%s" %(self.username) )
        print_debug ( "TcosDBusServer() admin=\"%s\" passwd=\"%s\""  %(self.admin, self.passwd) )
        self.bus = dbus.SystemBus()

    def auth(self):
        print_debug ( "self.admin=%s self.passwd=%s" %(self.admin, self.passwd) )
        if not self.admin or not self.passwd:
            #self.error_msg=_("Need admin and passwd data to do this action")
            print_debug ( "Need admin and passwd data to do this action" )
            return False
        
        
        # get DISPLAY env var
        self.host, display=os.environ["DISPLAY"].split(':')
        self.display = ":%s" %(display)
        print_debug( "host=\"%s\" display=\"%s\"" %(self.host, self.display) )
        
        #  FIXME
        #  to TEST and DEBUG
        #
        #self.host="tcos11"
        #
        #
        
        if self.host == "" and not shared.allow_local_display:
            self.error_msg=_("TcosDBus not allowed in local display")
            print_debug ( "auth() not allowed in local display" )
            return False
        
        # for standalone use hostname as self.host
        if self.host == "":
            import socket
            self.host=socket.gethostname()
            
        
        
        # check if tcosxmlrpc is running
        from ping import PingPort
        status=PingPort(self.host, shared.xmlremote_port).get_status()
        print_debug ( "isPortListening() status=%s" %(status) )
        
        if status == "CLOSED" or status == "ERROR":
            print_debug ( "auth() seems that tcosxmlrpc isn't running on host=\"%s\"" %(self.host) )
            self.error_msg=_("Seems that tcosxmlrpc isn't running on host=\"%s\"" %(self.host) )
            return False
        else:
            print_debug ("auth() status=%s" %(status))
           
        # check tcosxmlrpc username and pass
        if not self.connect_tcosxmlrpc(self.host):
            print_debug ( "auth() tcosxmlrpc says access denied" )
            return False
        
        # if here grant access
        return True

    def connect_tcosxmlrpc(self, host):
        self.url = 'http://%s:%d/RPC2' %(host, shared.xmlremote_port)
        print_debug ( "connect_tcosxmlrpc() url=%s" %(self.url) )
        try:
            import xmlrpclib
            self.tc = xmlrpclib.Server(self.url)
            print_debug ( "connect_tcosxmlrpc() tcosxmlrpc running on %s" %(host) )
        except:
            self.error_msg=_("tcosxmlrpc ERROR conection unavalaible." )
            print_debug("connect_tcosxmlrpc() ERROR conection unavalaible !!!")
            return False
        
        cmd= "uname"
        # try to exec something
        print_debug("connect_tcosxmlrpc() try to exec \"%s\" " %(cmd) )
        result=self.tc.tcos.exe(cmd, self.admin, self.passwd)
        if result == cmd:
            print_debug ( "connect_tcosxmlrpc() cmd run OK." )
            return True
        else:
            self.error_msg=_("ERROR conecting to tcosxmlrpc, check username and password." )
            print_debug ( "error connecting: %s" %(result) )
            return False

    def send_error_msg(self):
        #FIXME, how to return error message ???
        pass

    def parse_dbus_str(self, data):
        print_debug( "parse_dbus_str() data=%s type=%s" %(data, type(data)) )
        if type(data) == dbus.String:
            return str(data)
        return(data)
            
    def new_message(self, message):
        print_debug ( "new_message() %s" %(message) )

        self.admin = self.parse_dbus_str(message[0][0])
        self.passwd = self.parse_dbus_str(message[0][1])
        if not self.auth():
            self.send_error_msg()
            return
        
        for user in message[1]:
            print_debug ("new_message() loop users => user=%s" %(user) )
            if user == self.username:
                msg_type=self.parse_dbus_str(message[2][0])
                msg_args=self.parse_dbus_str(message[3][0])
                print_debug ( "new_message() Ummm one message for me!!" )
                print_debug ( "type=%s args=%s" %(msg_type, msg_args) )
                
                if msg_type == "kill":
                    pid=int(msg_args)
                    self.user_kill(pid)
                if msg_type == "killall":
                    self.user_killall(msg_args)
                elif msg_type == "exec":
                    self.user_exec(msg_args)
                elif msg_type == "mess":
                    self.user_msg(msg_args)
                else:
                    print_debug ( "new_message() ERROR, unknow type of message=\"%s\"" %(msg_type) )
                print_debug ( "new_message() finish !!!" )

    def user_kill(self, pid):
        print_debug ( "user_kill() %s" %(pid) )
        pid=int(pid)
        try:
            os.kill(pid, signal.SIGKILL)
        except:
            print_debug ( "user_kill() error, pid not found %d" %(pid) )
        return
    
    def user_killall(self, app):
        print_debug ( "user_killall() %s" %(app) )
        subprocess.Popen("killall %s" %(app), shell=True)
        return
        
    def user_exec(self, cmd):
        print_debug ( "user_exec() %s" %(cmd) )
        subprocess.Popen(cmd, shell=True)
        return
        
    def user_msg(self, txt):
        print_debug ( "user_msg() %s" %(txt) )
        subprocess.Popen(['zenity', '--info', '--text=' + txt + ' ', '--title='+_("Message from admin")])
        return
    
    def start(self):
        #iface.connect_to_signal('hello_signal', new_message)
        self.bus.add_signal_receiver(self.new_message,
                        signal_name='GotSignal',
                        dbus_interface='com.consoltux.TcosMonitor.Comm',
                        path='/TCOSObject')
                        
        mainloop = gobject.MainLoop()
        mainloop.run()


class TcosDBusClient(dbus.service.Object):
    def __init__(self, bus_name, object_path="/TCOSObject"):
        print_debug ( "TcosDBusClient() starting client" )
        dbus.service.Object.__init__(self, bus_name, object_path)
        
    @dbus.service.signal("com.consoltux.TcosMonitor.Comm", signature="aas")    
    def GotSignal(self, message):
        pass

class TcosDBusAction:
    def __init__(self, main, admin="", passwd=""):
        print_debug ("TcosDBusAction() starting action...")
        self.admin=admin
        self.passwd=passwd
        self.connection = False
        self.error = None
        self.done = False
        self.main=main
        try:
            system_bus = dbus.SystemBus()
        except:
            self.error = "Error getting system bus. Is DBus running?"
            return
            
        try:
            name = dbus.service.BusName("com.consoltux.TcosMonitor", bus=system_bus)
        except:
            self.error = "Error getting name of TcosMonitor dbus, are you autorized?"
            return
            
        self.dbus_iface = TcosDBusClient(name)
        self.connection=True

    def get_error_msg(self):
        return self.error
        
    def do_exec(self, users, app):
        print_debug ( "do_exec() users=%s app=%s" %(users,app) )
        
        if self.main.xmlrpc.IsStandalone():
            return self.main.xmlrpc.DBus("exec", app)
        
        if not self.connection:
            print_debug ( self.error )
            return False
        try:
            self.dbus_iface.GotSignal( [ [self.admin, self.passwd], users , ["exec"] , [app] ])
            self.done = True
            
        except:
            self.error = _("User not allowed to run this dbus call.")
            print_debug ( "User not allowed to use dbus" )
            
        return self.done
        
    def do_message(self, users, text=""):
        print_debug ( "do_message() users=%s text=%s" %(users, text) )
        
        if self.main.xmlrpc.IsStandalone():
            return self.main.xmlrpc.DBus("mess", text)
        
        if not self.connection:
            print_debug ( self.error )
            return False
        try:
            self.dbus_iface.GotSignal( [ [self.admin, self.passwd], users , ["mess"] , [text] ])
            self.done = True
            
        except:
            self.error = _("User not allowed to run this dbus call.")
            print_debug ( "User not allowed to use dbus" )
            
        return self.done
    
    def do_kill(self, users, pid="0"):
        print_debug ( "do_kill() users=%s pid=%s" %(users, pid) )
        
        if self.main.xmlrpc.IsStandalone():
            return self.main.xmlrpc.DBus("kill", text)
        
        
        if not self.connection:
            print_debug ( self.error )
            return False
        
        #self.dbus_iface.GotSignal( [ [self.admin, self.passwd], users , ["kill"] , [pid] ])
        try:
            print_debug ( "send signal" )
            self.dbus_iface.GotSignal( [ [self.admin, self.passwd], users , ["kill"] , [pid] ])
            self.done = True
            
        except:
            self.error = _("User not allowed to run this dbus call.")
            print_debug ( "User not allowed to use dbus" )
            
        return self.done

    def do_killall(self, users, proc=""):
        print_debug ( "do_kill() users=%s proc=%s" %(users, proc) )
        
        if self.main.xmlrpc.IsStandalone():
            return self.main.xmlrpc.DBus("killall", proc)
        
        if not self.connection:
            print_debug ( self.error )
            return False
        
        #self.dbus_iface.GotSignal( [ [self.admin, self.passwd], users , ["kill"] , [pid] ])
        try:
            print_debug ( "send signal" )
            self.dbus_iface.GotSignal( [ [self.admin, self.passwd], users , ["killall"] , [proc] ])
            self.done = True
            
        except:
            self.error = _("User not allowed to run this dbus call.")
            print_debug ( "User not allowed to use dbus" )
            
        return self.done            


if __name__ == "__main__":
    shared.debug=True
    if len(sys.argv) < 2:
        print ( "Need --server or --client param " )
        sys.exit(1)
    
    if sys.argv[1] == "--server":
        print_debug ("starting server")
        server=TcosDBusServer().start()
        
    if sys.argv[1] == "--client":
        action=TcosDBusAction(admin="root", passwd="root")
        result = action.do_message( ["mario"] , "Test message from dbus interface")
        if not result:
            print action.get_error_msg()
            
        #result = action.do_exec( ["prueba"] , "xterm")
        #if not result:
        #    print action.get_error_msg()
            
        #result = action.do_kill( ["mario"] , "9146")
        #if not result:
        #    print action.get_error_msg()
        



        
