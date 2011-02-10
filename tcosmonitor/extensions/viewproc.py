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
""" template extension """

from gettext import gettext as _
import sys

from tcosmonitor import shared
from tcosmonitor.TcosExtensions import TcosExtension

import gtk

def print_debug(txt):
    if shared.debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)


class ViewProc(TcosExtension):
    def register(self):
        self.main.menus.register_simple( _("Show running apps of this client") , "menu_proc.png", 1, self.viewproc, "show")
        

    def viewproc(self, widget, ip):
        if not self.get_client():
            return
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg ( _("Can't show runnings apps, user is not logged") )
            return
        self.get_user_processes(ip)


    def get_user_processes(self, ip):
        """get user processes in session"""
        print_debug( "get_user_processes(%s) __init__" %ip )
        #check user is connected
        if not self.main.localdata.IsLogged(ip):
            shared.info_msg( _("User not connected, no processes.") )
            return
        
        
        if self.main.xmlrpc.IsStandalone(ip):
            username=self.main.localdata.GetUsernameAndHost(ip)
            tmp=self.main.xmlrpc.ReadInfo("get_process")
            if tmp != "":
                process=tmp.split('|')[0:-1]
            else:
                process=["PID COMMAND", "66000 can't read process list"]
        else:    
            username=self.main.localdata.GetUsername(ip)
            cmd="LANG=C ps U \"%s\" -o pid,command | /usr/lib/tcos/clean_string.sh " %(self.main.localdata.GetUserID(username))
            print_debug ( "get_user_processes(%s) cmd=%s " %(ip, cmd) )
            process=self.main.common.exe_cmd(cmd, verbose=0)
        
        self.main.datatxt.clean()
        self.main.datatxt.insert_block(   _("Running processes for user \"%s\": " ) %(username), image=shared.IMG_DIR + "info_proc.png"  )
        
        if self.main.config.GetVar("systemprocess") == "0":
            self.main.datatxt.insert_block ( \
            _("ALERT: There are some system process hidden. Enable it in Preferences dialog.") \
            , image=shared.IMG_DIR + "icon_alert.png" ,\
            color="#f08196", size="medium" )
        
        self.main.datatxt.insert_html ( """
        <br/><div style='margin-left: 135px; margin-right: 200px;background-color:#ead196;color:blue'>""" + _("Pid") + "\t" 
        + "\t" + _("Process command") +"</div>" )
        
        counter=0
        self.main.kill_proc_buttons=None
        self.main.kill_proc_buttons=[]
        blabel=_("Kill this process")
        
        for proc in process:
            is_hidden=False
            if proc.split()[0]== "PID":
                continue
            pid=proc.split()[0] # not convert to int DBUS need string
            name=" ".join(proc.split()[1:])
            name=name.replace('<','&lt;').replace('>','&gt;')
            name=name.replace('&','&amp;')
            
            if int(self.main.config.GetVar("systemprocess")) == 0:
                for hidden in shared.system_process:
                    if hidden in name:
                        is_hidden=True
            
            if is_hidden:
                continue
            
            kill_button=gtk.Button(label=blabel)
            kill_button.connect("clicked", self.on_kill_button_click, pid, username)
            kill_button.show()
            self.main.kill_proc_buttons.append(kill_button)
                    
            self.main.datatxt.insert_html("""
            <span style='background-color: red; margin-left: 5px; margin-right: 0px'>
            <input type='button' name='self.main.kill_proc_buttons' index='%d' label='%s' /></span>
            <span style='color: red; margin-left: 140px; margin-right: 0px'> %6s</span>
            <span style='color: blue; margin-left: 350px; margin-right: 0px'> %s</span><br />
            """ %(counter, blabel, pid, name) )
            counter+=1
        
        self.main.datatxt.display()
        return

    def on_kill_button_click(self, widget, pid, username):
        print_debug ( "on_kill_button_click() pid=%s username=%s" %(pid, username) )
        if shared.ask_msg ( _("Are you sure you want to stop this process?") ):
            print_debug ( "KILL KILL KILL" )
            if username.find(":") != -1 :
                usern, ip = username.split(":")
                self.main.xmlrpc.newhost(ip)
                self.main.xmlrpc.DBus("kill", str(pid) )
            else:
                result = self.main.dbus_action.do_kill( [username] , str(pid) )
                if not result:
                    shared.error_msg ( _("Error while killing app:\nReason: %s") %( self.main.dbus_action.get_error_msg() ) )
                else:
                    print_debug ( "on_kill_button_click() KILLED ;)" )
            self.get_user_processes(self.main.selected_ip)

__extclass__=ViewProc
