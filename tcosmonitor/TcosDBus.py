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

# dbus classes for tcosmonitor

import dbus
import dbus.service
import dbus.glib
import gobject
import os
import signal
import subprocess, threading
import pwd
import sys
from gettext import gettext as _
import pynotify
from time import sleep

# needed for __escape__ function
import xml.sax.saxutils

import tcosmonitor.shared
def print_debug(txt):
    if tcosmonitor.shared.debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)


class TcosDBusServer:
    def __init__(self):
        self.username = pwd.getpwuid(os.getuid())[0]
        self.admin=None
        self.passwd=None
        self.error_msg=None
        print_debug ( "TcosDBusServer() __init__ as username=%s" %(self.username) )
        print_debug ( "TcosDBusServer() admin='%s' passwd='*****'"  %(self.admin) )
        
        self.__dic__= {
             '\"'    :    '&quot;',
             '\''    :    '&apos;'
                      }

        
        import tcosmonitor.TcosCommon
        self.common=tcosmonitor.TcosCommon.TcosCommon(self)
        self.host=self.common.get_display(ip_mode=True)
        # in Ubuntu with NetworkManager probably don't have IP now, make a wait loop
        if self.host is None:
            while not self.host:
                print "TcosDBusServer: No IP found (%s) waiting..." % (self.host)
                sleep(3)
                self.host=self.common.get_display(ip_mode=True)
        # If here IP found get hostname
        self.hostname=self.common.get_display(ip_mode=False)
        
        self.bus = dbus.SystemBus()

    def auth(self):
        #print_debug ( "self.admin=%s self.passwd=%s" %(self.admin, self.passwd) )
        if not self.admin or not self.passwd:
            print_debug ( "Need admin and passwd data to do this action" )
            return False
        
        if self.host == "" and not tcosmonitor.shared.allow_local_display:
            self.error_msg=_("TcosDBus not allowed in local display")
            print_debug ( "auth() not allowed in local display" )
            return False

        import tcosmonitor.ping
        # for standalone use local ip as self.host
        if tcosmonitor.shared.allow_local_display:
            p=tcosmonitor.ping.Ping(None)
            ips=p.get_server_ips()
            if len(ips) < 1:
                print "tcos-dbus-client **WARNING** Can't get IP adrress, trying with hostname"
            else:
                if len(ips) > 1:
                    print "tcos-dbus-client **WARNING** This host have more than one IP: %s using first: %s" % (ips, ips[0])
                self.host=ips[0]
                     
        # is self.host is empty try with hostname
        if self.host == "":
            import socket
            self.host=socket.gethostname()
            
        
        # check if tcosxmlrpc is running
        status=tcosmonitor.ping.PingPort(self.host, tcosmonitor.shared.xmlremote_port).get_status()
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
        self.url = 'http://%s:%d/RPC2' % (host, tcosmonitor.shared.xmlremote_port)
        print_debug ( "connect_tcosxmlrpc() url=%s" %(self.url) )
        try:
            import xmlrpclib
            self.tc = xmlrpclib.Server(self.url)
            print_debug ( "connect_tcosxmlrpc() tcosxmlrpc running on %s" %(host) )
        except Exception, err:
            self.error_msg=_("tcosxmlrpc ERROR conection unavalaible." )
            print_debug("connect_tcosxmlrpc() ERROR conection unavalaible !!!, error=%s"%err)
            return False
        
        cmd= "uname"
        # try to exec something
        print_debug("connect_tcosxmlrpc() try to exec \"%s\" " %(cmd) )
        try:
            result=self.tc.tcos.exe(cmd, self.admin, self.passwd)
        except Exception, err:
            print_debug("connect_tcosxmlrpc() cmd error=%s"%err)
            
        if result == cmd:
            print_debug ( "connect_tcosxmlrpc() cmd run OK." )
            return True
        else:
            self.error_msg=_("ERROR conecting to tcosxmlrpc, check username and password." )
            print_debug ( "error connecting: %s" %(result) )
            return False

    def send_error_msg(self):
        #FIXME, how to return error message with dbus???
        pass

    def parse_dbus_str(self, data):
        #print_debug( "parse_dbus_str() data=%s type=%s" %(data, type(data)) )
        if isinstance(data, dbus.String):
            return str(data)
        return(data)
    
    def get_desktop_path(self):
        print_debug ( "get_desktop_path()")
        cmd="/usr/lib/tcos/get-xdg-desktop"
        try:
            p = subprocess.Popen(cmd, shell=True, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        except Exception, e:
            print_debug("Exception in subprocess cmd(%s), error='%s'"%(cmd, e))
            return None
        desktop=None
        try:
            result=p.stdout.readlines()
            for line in result:
                if line != '\n':
                    desktop=line.replace('\n', '')
        except Exception, e:
            print_debug("Exception in subprocess::readlines() cmd(%s), error='%s'"%(cmd, e))
            return None
        if not os.path.isdir(desktop):
            desktop=os.path.expanduser("~/Desktop")
        return desktop
         
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
                print_debug ( "new_message() Ummm one message for me!!" )
                if msg_type == "sendfiles":
                    tmp=[]
                    print_debug(message[3])
                    if " " in message[3][0]:
                        # standalone
                        # dbus.Array([dbus.String(u'Teacher 192.168.0.254 True')], signature=...)
                        tmp=self.parse_dbus_str(message[3][0]).split()
                    else:
                        # thin client
                        # dbus.Array([dbus.String(u'Teacher'), dbus.String(u'192.168.0.254'), dbus.String(u'True')], signature=...)
                        tmp=message[3]
                    msg_arg_1=self.parse_dbus_str(tmp[0])
                    msg_arg_2=self.parse_dbus_str(tmp[1])
                    msg_arg_3=self.parse_dbus_str(tmp[2])
                    print_debug ( "new_message() type=%s arg_1=%s arg_2=%s arg_3=%s" %(msg_type, msg_arg_1, msg_arg_2, msg_arg_3) )
                else:
                    msg_args=self.parse_dbus_str(message[3][0])
                    print_debug ( "new_message() type=%s args=%s" %(msg_type, msg_args) )
                
                if msg_type == "kill":
                    pid=int(msg_args)
                    self.user_kill(pid)
                if msg_type == "killall":
                    self.user_killall(msg_args)
                elif msg_type == "exec":
                    self.user_exec(msg_args)
                elif msg_type == "mess":
                    self.user_msg(msg_args)
                elif msg_type == "sendfiles":
                    self.user_sendfiles(msg_arg_1, msg_arg_2, msg_arg_3)  
                else:
                    print_debug ( "new_message() ERROR, unknow type of message=\"%s\"" %(msg_type) )
                print_debug ( "new_message() finish !!!" )

    def cleanproc(self, proc):
        try:
            os.waitpid(proc.pid, os.WCONTINUED)
        except os.error, err:
            print_debug("OSError exception: %s" %err)
    
    def user_kill(self, pid):
        print_debug ( "user_kill() %s" %(pid) )
        pid=int(pid)
        try:
            os.kill(pid, signal.SIGKILL)
        except Exception, err:
            print_debug ( "user_kill() error, pid not found %d, error=%s" %(pid, err) )
        return
    
    def user_killall(self, app):
        print_debug ( "user_killall() %s" %(app) )
        p = subprocess.Popen("killall -s KILL %s" %(app), shell=True, close_fds=True)
        try:
            th=threading.Thread(target=self.cleanproc, args=(p,) )
            #th.setDaemon(1)
            th.start()
            print_debug("Threads count: %s" %threading.activeCount())
        except Exception, err:
            print_debug ( "user_killall() error, error=%s" %(err) )
        return
        
    def user_exec(self, cmd):
        print_debug ( "user_exec() %s" %(cmd) )
        p = subprocess.Popen(cmd, shell=True, close_fds=True)
        try:
            th=threading.Thread(target=self.cleanproc, args=(p,) )
            #th.setDaemon(1)
            th.start()
            print_debug("Threads count: %s" %threading.activeCount())
        except Exception, err:
            print_debug ( "user_exec() error, error=%s" %(err) )
            #pass
        return
        
    def user_sendfiles(self, dir, server, openfile):
        print_debug ( "user_sendfiles() dir=%s server=%s open=%s" %(dir, server, openfile))
        desktop=self.get_desktop_path()
        local_dir=os.path.join(desktop, dir)
        cmd="/usr/lib/tcos/tcos-ftpclient --dir=%s --server=%s --open=%s" %(local_dir, server, openfile)
        print_debug("user_sendfiles() cmd=%s" %cmd)
        p = subprocess.Popen(cmd, shell=True, close_fds=True)
        try:
            th=threading.Thread(target=self.cleanproc, args=(p,) )
            #th.setDaemon(1)
            th.start()
            print_debug("Threads count: %s" %threading.activeCount())
        except Exception, err:
            print_debug ( "user_sendfiles() error, error=%s" %(err) )
            #pass
        return

    def __escape__(self, txt):
        return xml.sax.saxutils.escape(txt, self.__dic__)

    def user_msg(self, txt):
        print_debug ( "user_msg() %s" %(txt) )
        # use pynotify better???
        self.show_notification( self.__escape__( _("Message from admin") ), self.__escape__( txt ) )
#        p = subprocess.Popen("zenity --info --text='%s' --title='%s'" %(txt.replace("'", "´"), _("Message from admin").replace("'", "´")), shell=True, close_fds=True)
#        try:
#            th=threading.Thread(target=self.cleanproc, args=(p,) )
#            #th.setDaemon(1)
#            th.start()
#            print_debug("Threads count: %s" %threading.activeCount())
#        except Exception, err:
#            print_debug ( "user_msg() error, error=%s" %(err) )
#            pass
#        return

    def show_notification(self, title, msg, urgency=pynotify.URGENCY_CRITICAL):
        print_debug("show_notification() title='%s', msg='%s'" %(title, msg) )
        pynotify.init("tcosmonitor")
        if os.path.isfile("/usr/share/pixmaps/tcos-icon-32x32-custom.png"):
            image_uri="file://usr/share/pixmaps/tcos-icon-32x32-custom.png"
        else:
            image_uri="file://usr/share/pixmaps/tcos-icon-32x32.png"
        n = pynotify.Notification( title , msg, image_uri )
        n.set_urgency(urgency)
        n.set_category("TcosDBus")
        n.set_timeout(40000) # 15 sec
        if not n.show():
            print_debug  ("show_notification() Failed to send notification")

    def start(self):
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
        except Exception, err:
            self.error = "Error getting system bus. Is DBus running?"
            print_debug ( "TcosDbusAction::__init__() error, error=%s" %(err) )
            return
            
        try:
            name = dbus.service.BusName("com.consoltux.TcosMonitor", bus=system_bus)
        except Exception, err:
            self.error = "Error getting name of TcosMonitor dbus, are you autorized?"
            print_debug ( "TcosDbusAction::__init__() error, error=%s" %(err) )
            return
            
        self.dbus_iface = TcosDBusClient(name)
        self.connection=True

    def set_auth(self, admin, passwd):
        self.admin=admin
        self.passwd=passwd

    def get_error_msg(self):
        return self.error
        
    def do_sendfiles(self, users, dir, server, open):
        print_debug ( "do_sendfiles() users=%s dir=%s server=%s open=%s" %(users, dir, server, open) )
        
        if not self.connection:
            print_debug ( self.error )
            return False
        try:
            self.dbus_iface.GotSignal( [ [self.admin, self.passwd], users , ["sendfiles"] , [dir, server, open] ])
            self.done = True
            
        except Exception, err:
            self.error = _("User not allowed to run this dbus call.")
            print_debug ( "User not allowed to use dbus, error=%s"%err )
            
        return self.done
        
    def do_exec(self, users, app):
        print_debug ( "do_exec() users=%s app=%s" %(users, app) )
        
        if not self.connection:
            print_debug ( self.error )
            return False
        try:
            self.dbus_iface.GotSignal( [ [self.admin, self.passwd], users , ["exec"] , [app] ])
            self.done = True
            
        except Exception, err:
            self.error = _("User not allowed to run this dbus call.")
            print_debug ( "User not allowed to use dbus, error=%s"%err )
            
        return self.done
        
    def do_message(self, users, text=""):
        print_debug ( "do_message() users=%s text='%s'" %(users, text) )
        
        if not self.connection:
            print_debug ( self.error )
            return False
        try:
            self.dbus_iface.GotSignal( [ [self.admin, self.passwd], users , ["mess"] , [text] ])
            self.done = True
            
        except Exception, err:
            self.error = _("User not allowed to run this dbus call.")
            print_debug ( "User not allowed to use dbus, error=%s"%err )
            
        return self.done
    
    def do_kill(self, users, pid="0"):
        print_debug ( "do_kill() users=%s pid=%s" %(users, pid) )
        
        if not self.connection:
            print_debug ( self.error )
            return False
        
        try:
            print_debug ( "send signal" )
            self.dbus_iface.GotSignal( [ [self.admin, self.passwd], users , ["kill"] , [pid] ])
            self.done = True
            
        except Exception, err:
            self.error = _("User not allowed to run this dbus call.")
            print_debug ( "User not allowed to use dbus, error=%s"%err )
            
        return self.done

    def do_killall(self, users, proc=""):
        print_debug ( "do_kill() users=%s proc=%s" %(users, proc) )
        
        if not self.connection:
            print_debug ( self.error )
            return False
        
        try:
            print_debug ( "send signal" )
            self.dbus_iface.GotSignal( [ [self.admin, self.passwd], users , ["killall"] , [proc] ])
            self.done = True
            
        except Exception, err:
            self.error = _("User not allowed to run this dbus call.")
            print_debug ( "User not allowed to use dbus, error=%s"%err )
            
        return self.done            


if __name__ == "__main__":
    tcosmonitor.shared.debug=True
    if len(sys.argv) < 2:
        print ( "Need --server or --client param " )
        sys.exit(1)
    
    if sys.argv[1] == "--server":
        print_debug ("starting server")
        server=TcosDBusServer().start()
        
    if sys.argv[1] == "--client":
        action=TcosDBusAction(admin="root", passwd="root")
        result2 = action.do_message( ["mario"] , "Test message from dbus interface")
        if not result2:
            print action.get_error_msg()
            
        #result = action.do_exec( ["prueba"] , "xterm")
        #if not result:
        #    print action.get_error_msg()
            
        #result = action.do_kill( ["mario"] , "9146")
        #if not result:
        #    print action.get_error_msg()
        



        
