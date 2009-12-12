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

from tcosmonitor import shared
from tcosmonitor.TcosExtensions import TcosExtension

import os
from random import Random
from time import sleep
import string
import subprocess
import signal

from tcosmonitor.ping import PingPort

import gtkvnc
import gtk
import traceback
import sys

def print_debug(txt):
    if shared.debug:
        print "%s::%s" % ("extensions::vnc", txt)
    return


class VNC(TcosExtension):
    def register(self):
        self.vnc_count={}
        self.main.menus.register_simple( _("Connect to remote screen (VNC)"), "menu_remote.png", 1, self.vnc_simple, "vnc")
        self.main.menus.register_simple( _("Demo mode (from this host)") , "menu_tiza.png", 1, self.vnc_demo_simple, "demo")
        
        self.main.menus.register_all( _("Enter demo mode, all connected users see my screen") , "menu_tiza.png", 1, self.vnc_demo_all, "demo")
        self.vnc={}
        self.vncwindow={}
        self.is_fullscreen={}

    def vnc_demo_all(self, *args):
        if not self.get_all_clients():
            return
        # demo mode
        #generate password vnc
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg( _("No users logged.") )
            return
        
        msg=_( _("Do you want to start demo mode the following users: %s?" )%(self.connected_users_txt) )
                                                
        if not shared.ask_msg ( msg ):
            return
        
        passwd=''.join( Random().sample(string.letters+string.digits, 12) )
        self.main.common.exe_cmd("x11vnc -storepasswd %s %s >/dev/null 2>&1" \
                                %(passwd, os.path.expanduser('~/.tcosvnc')), verbose=0, background=True )
        
        # start x11vnc in local 
        p=subprocess.Popen(["x11vnc", "-shared", "-noshm", "-viewonly", "-forever", "-rfbauth", "%s" %( os.path.expanduser('~/.tcosvnc') ) ], shell=False, bufsize=0, close_fds=True)
        
        self.main.write_into_statusbar( _("Waiting for start demo mode...") )
        
        # need to wait for start, PingPort loop
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
            if len(self.vnc_count.keys()) != 0:
                count=len(self.vnc_count.keys())-1
                nextkey=self.vnc_count.keys()[count]+1
                self.vnc_count[nextkey]=None
            else:
                nextkey=1
                self.vnc_count[nextkey]=None
            self.add_progressbox( {"target": "vnc", "ip":"", "pid":p.pid, "allclients":self.newallclients, "key":nextkey}, _("Running in demo mode from server. Demo Nº %s") %(nextkey) )
        

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
                #cmd=("LC_ALL=C LC_MESSAGES=C vncviewer --version 2>&1| grep built |grep -c \"4.1\"")
                #output=self.main.common.exe_cmd(cmd)
                #if output == "1":
                #    cmd = ("vncviewer " + ip + " -UseLocalCursor=0 -passwd %s" %os.path.expanduser('~/.tcosvnc') )
                #else:
                #    cmd = ("vncviewer " + ip + " -passwd %s" %os.path.expanduser('~/.tcosvnc') )
                #print_debug ( "start_process() threading \"%s\"" %(cmd) )
                #self.main.common.exe_cmd (cmd, verbose=0, background=True)
                self.vncviewer(ip, passwd)
        except Exception, err:
            print_debug("start_vnc() Exception, error=%s"%err)
            traceback.print_exc(file=sys.stderr)
            self.main.common.threads_enter("TcosActions:start_vnc print x11vnc support msg")
            shared.error_msg ( _("Can't start VNC, please add X11VNC support") )
            self.main.common.threads_leave("TcosActions:start_vnc print x11vnc support msg")
            return

        self.main.common.threads_enter("TcosActions:start_vnc clean status msg")
        self.main.write_into_statusbar( "" )
        self.main.common.threads_leave("TcosActions:start_vnc clean status msg")

    def vncviewer_destroy(self, window, ip):
        try:
            self.vncwindow[ip].hide()
            self.vncwindow[ip].destroy()
        except Exception, err:
            print_debug("vncviewer_destroy() Cant hide/destroy vncviewer window, err=%s"%err)
        print_debug("vncviewer_destroy() self.vnc=%s"%self.vnc)
        if self.vnc.has_key(ip):
            self.vnc[ip].close()
            self.vnc.pop(ip)
        if self.vncwindow.has_key(ip):
            self.vncwindow.pop(ip)

    def vncviewer_fullcontrol(self, button, ip):
        image=gtk.Image()
        
        if self.vnc[ip].get_read_only():
            self.vnc[ip].set_read_only(False)
            button.set_label( _("Switch to view only") )
            image.set_from_stock('gtk-find', gtk.ICON_SIZE_BUTTON)
            button.set_image(image)
        else:
            self.vnc[ip].set_read_only(True)
            button.set_label( _("Switch to full control") )
            image.set_from_stock('gtk-find-and-replace', gtk.ICON_SIZE_BUTTON)
            button.set_image(image)

    def vncviewer_force_resize(self, vnc, size, ip):
        w,h = vnc.get_size_request()
        if w == -1 or h == -1:
            print_debug("_force_resize() returning w=%s h=%s ip=%s"%(w, h, ip))
            return
        vnc.set_size_request(w/2, h/2)


    def on_fullscreenbutton_click(self, button, ip):
        image=gtk.Image()
        if self.is_fullscreen[ip]:
            self.vncwindow[ip].unfullscreen()
            self.is_fullscreen[ip]=False
            image.set_from_stock('gtk-fullscreen', gtk.ICON_SIZE_BUTTON)
        else:
            self.vncwindow[ip].fullscreen()
            self.is_fullscreen[ip]=True
            image.set_from_stock('gtk-leave-fullscreen', gtk.ICON_SIZE_BUTTON)
        button.set_image(image)

    def vncviewer(self, ip, passwd, stoptarget=None, stopargs=None):
        self.vncwindow[ip] = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.vncwindow[ip].set_icon_from_file(shared.IMG_DIR + 'tcos-icon-32x32.png')
        self.vncwindow[ip].set_title( _("VNC host %s") %(ip) )
        self.vncwindow[ip].connect("destroy", self.vncviewer_destroy, ip)
        box1 = gtk.HBox(True, 10)
        
        button = gtk.Button( _("Switch to full control") )
        button.connect("clicked", self.vncviewer_fullcontrol, ip)
        image=gtk.Image()
        image.set_from_stock('gtk-find-and-replace', gtk.ICON_SIZE_BUTTON)
        button.set_image(image)
        box1.pack_start(button, False, False, 0)
        button.show_all()

        fbutton = gtk.Button( _("Switch to fullscreen") )
        fbutton.connect("clicked", self.on_fullscreenbutton_click, ip)
        image=gtk.Image()
        image.set_from_stock('gtk-fullscreen', gtk.ICON_SIZE_BUTTON)
        fbutton.set_image(image)
        box1.pack_start(fbutton, False, False, 0)
        fbutton.show_all()

        if stoptarget:
            sbutton = gtk.Button( _("Stop") )
            sbutton.connect("clicked", stoptarget, stopargs, None)
            image=gtk.Image()
            image.set_from_stock('gtk-stop', gtk.ICON_SIZE_BUTTON)
            sbutton.set_image(image)
            box1.pack_start(sbutton, False, False, 0)
            sbutton.show_all()

        lastbutton = gtk.Button( _("Quit") )
        image=gtk.Image()
        image.set_from_stock('gtk-quit', gtk.ICON_SIZE_BUTTON)
        lastbutton.set_image(image)
        lastbutton.connect("clicked", self.vncviewer_destroy, ip)
        box1.pack_start(lastbutton, False, False, 0)
        lastbutton.show_all()
        
        self.vnc[ip]=gtkvnc.Display()
        self.vnc[ip].set_credential(gtkvnc.CREDENTIAL_PASSWORD, passwd)
        self.vnc[ip].set_credential(gtkvnc.CREDENTIAL_CLIENTNAME, self.main.name)
        
        #self.vnc[ip].connect("vnc-auth-credential", self._vnc_auth_cred, ip)
        self.vnc[ip].connect("size-request", self.vncviewer_force_resize, ip)
        #self.vnc[ip].connect("vnc-connected", self._vnc_connected, ip)
        # this freeze GUI, search another way
        #self.vnc[ip].set_tooltip_text("%s"%ip)
        
        self.vnc[ip].open_host(ip, '5900')
        self.vnc[ip].set_scaling(True)
        self.vnc[ip].set_read_only(True)
        self.vnc[ip].show()
        
        # Show the box
        box1.show()
        
        box2 = gtk.VBox(False, 0)
        box2.pack_start(box1, False, False, 0)
        box2.pack_start(self.vnc[ip], True, True, 0)
        
        
        # Show the window
        self.vncwindow[ip].add(box2)
        self.vncwindow[ip].show_all()
        self.is_fullscreen[ip]=False


    def vnc_demo_simple(self, widget, ip):
        if not self.get_client():
            return
        
        client_simple=self.connected_users_txt
            
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg ( _("Can't start demo mode, user is not logged") )
            return
            
        msg=_( _("Do you want demo mode from user %s?" ) %(client_simple) )
        if not shared.ask_msg ( msg ): return
        
        if self.main.iconview.ismultiple():
            self.allclients=self.main.iconview.get_multiple()
            
        elif self.main.classview.ismultiple():
            self.allclients=self.main.classview.get_multiple()
            
        elif self.main.listview.isactive() and self.main.config.GetVar("selectedhosts") == 1:
            self.allclients=self.main.listview.getmultiple()
            if len(self.allclients) == 0:
                self.allclients=self.main.localdata.allclients
        else:
            # get all clients connected
            self.allclients=self.main.localdata.allclients
            
        # Allow one client
        # if len(self.allclients) == 0: return
        
        # force kill x11vnc in client
        self.main.xmlrpc.newhost(ip)
        max_wait=5
        wait=0
        self.main.write_into_statusbar( _("Connecting with %s to start VNC support") %(client_simple) )
            
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
        
        self.main.write_into_statusbar( _("Waiting for start demo mode from user %s...") %(client_simple) )
            
        # need to wait for start, PingPort loop
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
            #cmd=("LC_ALL=C LC_MESSAGES=C vncviewer --version 2>&1| grep built |grep -c \"4.1\"")
            #output=self.main.common.exe_cmd(cmd)
            #if output == "1":
            #    p=subprocess.Popen(["vncviewer", ip, "-UseLocalCursor=0", "-PasswordFile", "%s" %os.path.expanduser('~/.tcosvnc')], shell=False, bufsize=0, close_fds=True)
            #else:
            #    p=subprocess.Popen(["vncviewer", ip, "-passwd", "%s" %os.path.expanduser('~/.tcosvnc')], shell=False, bufsize=0, close_fds=True)
            
            # new mode for stop button
            if len(self.vnc_count.keys()) != 0:
                count=len(self.vnc_count.keys())-1
                nextkey=self.vnc_count.keys()[count]+1
                self.vnc_count[nextkey]=None
            else:
                nextkey=1
                self.vnc_count[nextkey]=None
            
            stopargs={"target": "vnc", "ip": ip, "allclients":newallclients, "key":nextkey}
            self.vncviewer(ip, passwd, stoptarget=self.on_progressbox_click, stopargs=stopargs)
            #self.add_progressbox( {"target": "vnc", "pid":p.pid, "ip": ip, "allclients":newallclients, "key":nextkey}, _("Running in demo mode from user %(host)s. Demo Nº %(count)s") %{"host":client_simple, "count":nextkey} )
            self.add_progressbox( stopargs, _("Running in demo mode from user %(host)s. Demo Nº %(count)s") %{"host":client_simple, "count":nextkey} )

    def on_progressbox_click(self, widget, args, box):
        if box:
            box.destroy()
        else:
            for table in self.main.progressbox.get_children():
                #[<gtk.Label>, <gtk.Button>]
                # read key from label
                tlabel=table.get_children()[0]
                tbutton=table.get_children()[1]
                key=int(tlabel.get_text().split('Nº ')[1])
                if args['key'] == key:
                    # we have found IP in label !!! destroy table
                    table.destroy()
                    widget=tbutton
        print_debug("on_progressbox_click() widget=%s, args=%s, box=%s" %(widget, args, box) )
        
        if not args['target']: return

        try:
            self.main.stop_running_actions.remove(widget)
        except Exception, err:
            print_debug("on_progressbox_click() can't remove widget=%s err=%s"%(widget, err))
        
        if args['target'] == "vnc":
            del self.vnc_count[args['key']]
            if args['ip'] != "":
                for client in args['allclients']:
                    self.main.localdata.newhost(client)
                    if self.main.localdata.IsLogged(client):
                        self.main.xmlrpc.newhost(client)
                        self.main.xmlrpc.vnc("stopclient", client)
                # kill only in server one vncviewer
                #if "pid" in args:
                #    os.kill(args['pid'], signal.SIGKILL)
                #else:
                #    self.main.common.exe_cmd("killall -s KILL vncviewer", verbose=0, background=True)
                
                self.vncviewer_destroy(None, args['ip'])
                
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






