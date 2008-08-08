# -*- coding: UTF-8 -*-
##########################################################################
# TcosMonitor writen by MarioDebian <mariodebian@gmail.com>
#
#    TcosMonitor version __VERSION__
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
""" template extension """

from gettext import gettext as _

import shared
from TcosExtensions import TcosExtension, Error
import os
from random import Random
from time import sleep
import string
import subprocess
import signal

def print_debug(txt):
    if shared.debug:
        print "%s::%s" %("extensions::vnc", txt)
    return


class VNC(TcosExtension):
    def register(self):
        self.main.menus.register_simple( _("Connect to remote screen (VNC)"), "menu_remote.png", 1, self.vnc_simple)
        self.main.menus.register_simple( _("Demo mode (from this host)") , "menu_tiza.png", 1, self.vnc_demo_simple)
        
        self.main.menus.register_all( _("Enter demo mode, all connected users see my screen") , "menu_tiza.png", 1, self.vnc_demo_all)
        

    def vnc_demo_all(self, *args):
        if not self.get_all_clients():
            return
        # demo mode
        #generate password vnc
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg( _("No users logged.") )
            return
        
        msg=_( _("Do you want to start demo mode the following users:%s?" )%(self.newallclients_txt) )
                                                
        if not shared.ask_msg ( msg ):
            return
        
        passwd=''.join( Random().sample(string.letters+string.digits, 12) )
        self.main.common.exe_cmd("x11vnc -storepasswd %s %s >/dev/null 2>&1" \
                                %(passwd, os.path.expanduser('~/.tcosvnc')), verbose=0, background=True )
        
        # start x11vnc in local 
        p=subprocess.Popen(["x11vnc", "-shared", "-noshm", "-viewonly", "-forever", "-rfbauth", "%s" %( os.path.expanduser('~/.tcosvnc') ) ], shell=False, bufsize=0, close_fds=True)
        
        self.main.write_into_statusbar( _("Waiting for start demo mode...") )
        
        # need to wait for start, PingPort loop
        from ping import PingPort
        status = "CLOSED"
        max_wait=10
        wait=0
        while status != "OPEN":
            status=PingPort("127.0.0.1", 5900).get_status()
            if status == "CLOSED":
                sleep(1)
                wait+=1
            if wait > max_wait:
                break
        
        if status != "OPEN":
            self.main.write_into_statusbar( _("Error while exec app"))
            return
        
        total=0
        for client in self.newallclients:
            self.main.xmlrpc.vnc("genpass", client, passwd )
            # get server ip
            server_ip=self.main.xmlrpc.GetStandalone("get_server")
            print_debug("menu_event_all() vnc server ip=%s" %(server_ip))
            # start vncviewer
            self.main.xmlrpc.vnc("startclient", client, server_ip )
            total+=1
        
        if total < 1:
            self.main.write_into_statusbar( _("No users logged.") )
            # kill x11vnc
            os.kill(p.pid, signal.SIGKILL)
        else:
            self.main.write_into_statusbar( _("Running in demo mode with %s clients.") %(total) )
            #server_ip=self.main.xmlrpc.GetStandalone("get_server")
            #hostname=self.main.localdata.GetHostname(server_ip)
            # new mode Stop Button
            self.add_progressbox( {"target": "vnc", "ip":"", "pid":p.pid, "allclients":self.newallclients}, _("Running in demo mode from server") )
        

    def vnc_simple(self, w, ip):
        if not self.get_client():
            return
        
        if len(self.allclients_logged) == 0:
            shared.error_msg( _("No user logged.") )
            return
        
        self.main.worker=shared.Workers(self.main, target=self.start_vnc, args=(self.allclients_logged) )
        self.main.worker.start()

    def start_vnc(self, ip):
        # force kill x11vnc in client
        self.main.xmlrpc.newhost(ip)
        host=self.main.localdata.GetHostname(self.main.selected_ip)
        from ping import PingPort
        max_wait=5
        wait=0
        self.main.common.threads_enter("TcosActions:start_vnc print status msg")
        self.main.write_into_statusbar( _("Connecting with %s to start VNC support") %(host) )
        self.main.common.threads_leave("TcosActions:start_vnc print status msg")
            
        status="OPEN"
        while status != "CLOSED":
            status=PingPort(ip, 5900).get_status()
            self.main.xmlrpc.vnc("stopserver", ip )
            print_debug("start_vnc() waiting to kill x11vnc...")    
            sleep(1)
            wait+=1
            if wait > max_wait:
                print_debug("max_wait, returning")
                # fixme show error message
                return
        
        # gen password in thin client
        passwd=''.join( Random().sample(string.letters+string.digits, 12) )
        
        self.main.xmlrpc.vnc("genpass", ip, passwd)
        os.system("x11vnc -storepasswd %s %s >/dev/null 2>&1" \
                    %(passwd, os.path.expanduser('~/.tcosvnc')) )
                
        try:
            
            # before starting server, vnc-controller.sh exec killall x11vnc, not needed to stop server
            #self.main.xmlrpc.vnc("stopserver", ip )
            result=self.main.xmlrpc.vnc("startserver", ip)
            if result.find("error") != -1:
                self.main.common.threads_enter("TcosActions:start_vnc print error msg")
                shared.error_msg ( _("Can't start VNC, error:\n%s") %(result) )
                self.main.common.threads_leave("TcosActions:start_vnc print error msg")
                return
            self.main.common.threads_enter("TcosActions:start_vnc print waiting msg")
            self.main.write_into_statusbar( _("Waiting for start of VNC server...") )
            self.main.common.threads_leave("TcosActions:start_vnc print waiting msg")
            
            # need to wait for start, PingPort loop
            
            status = "CLOSED"
            
            wait=0
            while status != "OPEN":
                status=PingPort(ip, 5900).get_status()
                if status == "CLOSED":
                    sleep(1)
                    wait+=1
                if wait > max_wait:
                    break
            if status == "OPEN":
                cmd=("LC_ALL=C LC_MESSAGES=C vncviewer --version 2>&1| grep built |grep -c \"4.1\"")
                output=self.main.common.exe_cmd(cmd)
                if output == "1":
                    cmd = ("vncviewer " + ip + " -UseLocalCursor=0 -passwd %s" %os.path.expanduser('~/.tcosvnc') )
                else:
                    cmd = ("vncviewer " + ip + " -passwd %s" %os.path.expanduser('~/.tcosvnc') )
                print_debug ( "start_process() threading \"%s\"" %(cmd) )
                self.main.common.exe_cmd (cmd, verbose=0, background=True)
        except Exception, err:
            print_debug("start_vnc() Exception, error=%s"%err)
            self.main.common.threads_enter("TcosActions:start_vnc print x11vnc support msg")
            shared.error_msg ( _("Can't start VNC, please add X11VNC support") )
            self.main.common.threads_leave("TcosActions:start_vnc print x11vnc support msg")
            return

        self.main.common.threads_enter("TcosActions:start_vnc clean status msg")
        self.main.write_into_statusbar( "" )
        self.main.common.threads_leave("TcosActions:start_vnc clean status msg")


    def vnc_demo_simple(self, widget, ip):
        if not self.get_client():
            return
            
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg ( _("Can't start demo mode, user is not logged") )
            return
            
        msg=_( _("Do you want demo mode from %s?" ) %(self.host) )
        if not shared.ask_msg ( msg ): return
            
        if self.main.listview.isactive() and self.main.config.GetVar("selectedhosts") == 1:
            self.allclients=self.main.listview.getmultiple()
            if len(self.allclients) == 0:
                msg=_( _("No clients selected, do you want to select all?" ) )
                if shared.ask_msg ( msg ):
                    allclients=self.main.localdata.allclients
        else:
            # get all clients connected
            self.allclients=self.main.localdata.allclients
            
        if len(self.allclients) == 0: return
        
        # force kill x11vnc in client
        self.main.xmlrpc.newhost(ip)
        from ping import PingPort
        max_wait=5
        wait=0
        self.main.write_into_statusbar( _("Connecting with %s to start VNC support") %(ip) )
            
        status="OPEN"
        while status != "CLOSED":
            status=PingPort(ip, 5900).get_status()
            self.main.xmlrpc.vnc("stopserver", ip )
            print_debug("start_vnc() waiting to kill x11vnc...")    
            sleep(1)
            wait+=1
            if wait > max_wait:
                print_debug("max_wait, returning")
                # fixme show error message
                return
                    
        #generate password vnc
        passwd=''.join( Random().sample(string.letters+string.digits, 12) )
        self.main.common.exe_cmd("x11vnc -storepasswd %s %s >/dev/null 2>&1" \
                                %(passwd, os.path.expanduser('~/.tcosvnc')), verbose=0, background=True )
            
        # start x11vnc in remote host
        self.main.xmlrpc.vnc("genpass", ip, passwd )
        self.main.xmlrpc.vnc("startserver", ip )
        
        self.main.write_into_statusbar( _("Waiting for start demo mode from host %s...") %(ip) )
            
        # need to wait for start, PingPort loop
        from ping import PingPort
        status = "CLOSED"
        max_wait=10
        wait=0
        while status != "OPEN":
            status=PingPort(ip, 5900).get_status()
            if status == "CLOSED":
                sleep(1)
                wait+=1
            if wait > max_wait:
                break
            
        if status != "OPEN":
            self.main.write_into_statusbar( _("Error while exec app"))
            return
                    
        # start in 1 (teacher)
        newallclients=[]
        total=1
        for client in self.allclients:
            self.main.localdata.newhost(client)
            if self.main.localdata.IsLogged(client) and client != ip:
                self.main.xmlrpc.vnc("genpass", client, passwd )
                self.main.xmlrpc.vnc("startclient", client, ip )
                total+=1
                newallclients.append(client)
                
        if total < 1:
            self.main.write_into_statusbar( _("No users logged.") )
            # kill x11vnc in host
            self.main.xmlrpc.vnc("stopserver", ip )
        else:
            self.main.write_into_statusbar( _("Running in demo mode with %s clients.") %(total) )
            cmd=("LC_ALL=C LC_MESSAGES=C vncviewer --version 2>&1| grep built |grep -c \"4.1\"")
            output=self.main.common.exe_cmd(cmd)
            if output == "1":
                p=subprocess.Popen(["vncviewer", ip, "-UseLocalCursor=0", "-PasswordFile", "%s" %os.path.expanduser('~/.tcosvnc')], shell=False, bufsize=0, close_fds=True)
            else:
                p=subprocess.Popen(["vncviewer", ip, "-passwd", "%s" %os.path.expanduser('~/.tcosvnc')], shell=False, bufsize=0, close_fds=True)
            # new mode for stop button
            self.add_progressbox( {"target": "vnc", "pid":p.pid, "ip": ip, "allclients":newallclients}, _("Running in demo mode from host %s...") %(self.host) )


    def on_progressbox_click(self, widget, args, box):
        box.destroy()
        print_debug("on_progressbox_click() widget=%s, args=%s, box=%s" %(widget, args, box) )
        
        if not args['target']: return
        
        if args['target'] == "vnc":
            if args['ip'] != "":
                for client in args['allclients']:
                    self.main.localdata.newhost(client)
                    if self.main.localdata.IsLogged(client):
                        self.main.xmlrpc.newhost(client)
                        self.main.xmlrpc.vnc("stopclient", client)
                # kill only in server one vncviewer
                if "pid" in args:
                    os.kill(args['pid'], signal.SIGKILL)
                else:
                    self.main.common.exe_cmd("killall -s KILL vncviewer", verbose=0, background=True)
                self.main.xmlrpc.newhost(args['ip'])
                self.main.xmlrpc.vnc("stopserver", args['ip'] )
            else:
                # get all users at this demo mode and not kill others demo modes, in some cases need SIGKILL
                for client in args['allclients']:
                    self.main.localdata.newhost(client)
                    if self.main.localdata.IsLogged(client):
                        self.main.xmlrpc.newhost(client)
                        self.main.xmlrpc.vnc("stopclient", client)
                if "pid" in args:
                    os.kill(args['pid'], signal.SIGKILL)
                else:
                    self.main.common.exe_cmd("killall -s KILL x11vnc", verbose=0, background=True)
                
            self.main.write_into_statusbar( _("Demo mode off.") )
        



__extclass__=VNC






