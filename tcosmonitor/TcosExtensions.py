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

import shared
import os
import sys
import exceptions
from gettext import gettext as _
import gtk
import socket

def print_debug(txt):
    if shared.debug:
        print "%s::%s" % (__name__, txt)

class Error(exceptions.Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        shared.error_msg( _("Exception:") + "\n" + "="*40 + "\n\nError:\n" + self.msg )
        return "<Error : %s>" % self.msg
    __repr__ = __str__
    def __call__(self):
        return (self.msg,)


class TcosExtension(object):
    def __init__(self, main):
        #print_debug("__init__()")
        if not main:
            raise Error, "self.main not defined"
        
        self.main=main
        self.preferences={}
    
    def register(self):
        raise Error, "TcosExtension register() not defined"
    
    def get_client(self):
        if self.main.iconview.isactive():
            self.main.selected_ip=self.main.iconview.get_selected()
            self.main.selected_host=self.main.iconview.get_host(self.main.selected_ip)
        elif self.main.classview.isactive():
            self.main.selected_ip=self.main.classview.get_selected()
            self.main.selected_host=self.main.classview.get_host(self.main.selected_ip)
        else:
            self.main.selected_ip=self.main.listview.get_selected()
            self.main.selected_host=self.main.listview.get_host(self.main.selected_ip)
        
        if not self.main.selected_ip:
            # show a msg
            shared.error_msg ( _("Error: no IP!") )
            return False
        
        self.connected_users=[]
        self.connected_users_txt=""
        self.connected_users_txt_all=""
        self.newallclients=[]
        self.allclients_logged=[]
        self.main.localdata.newhost(self.main.selected_ip)
        self.main.xmlrpc.newhost(self.main.selected_ip)
        self.client_type = self.main.xmlrpc.ReadInfo("get_client")
        self.host=self.main.localdata.GetHostname(self.main.selected_ip)
        counter=1
        counter_all=1
        if self.main.localdata.IsLogged(self.main.selected_ip):
            username=self.main.localdata.GetUsernameAndHost(self.main.selected_ip)
            if username.find(":") != -1:
                usern, ip = username.split(":")
                self.connected_users_txt+="%s, " %(usern)
                self.connected_users_txt_all+="%s, " %(usern)
            else:
                self.connected_users_txt+="%s, " %(username)
                self.connected_users_txt_all+="%s, " %(username)
            self.connected_users.append(username)
            if counter % 4 == 0:
                self.connected_users_txt+="\n"
            if counter_all % 4 == 0:
                self.connected_users_txt_all+="\n"
            counter=int(counter+1)
            counter_all=int(counter_all+1)
            self.newallclients.append(self.main.selected_ip)
            self.allclients_logged.append(self.main.selected_ip)
        elif not self.main.xmlrpc.IsStandalone(self.main.selected_ip):
            self.allclients_logged.append(self.main.selected_ip)
            self.connected_users_txt_all+="%s, " %(self.main.selected_ip)
            if counter_all % 4 == 0:
                self.connected_users_txt_all+="\n"
            counter_all=int(counter_all+1)
        else:
            self.connected_users_txt_all+="%s, " %(self.main.selected_ip)
            if counter_all % 4 == 0:
                self.connected_users_txt_all+="\n"
            counter_all=int(counter_all+1)

        if self.connected_users_txt[-2:] == "\n": self.connected_users_txt=self.connected_users_txt[:-2]
        if self.connected_users_txt[-2:] == ", ": self.connected_users_txt=self.connected_users_txt[:-2]

        if self.connected_users_txt_all[-2:] == "\n": self.connected_users_txt_all=self.connected_users_txt_all[:-2]
        if self.connected_users_txt_all[-2:] == ", ": self.connected_users_txt_all=self.connected_users_txt_all[:-2]
        
        print_debug("get_clients() self.main.selected_ip=%s self.main.selected_host=%s"%(self.main.selected_ip, self.main.selected_host) )
        return True
        #if not self.doaction_onthisclient(action, self.main.selected_ip):
        #    # show a msg
        #    shared.info_msg ( _("Can't exec this action because you are connected at this host!") )
        #    return

########################################################################################


    def get_all_clients(self):
        # don't make actions in clients not selected
        if self.main.iconview.ismultiple():
            allclients=self.main.iconview.get_multiple()
            
        elif self.main.classview.ismultiple():
            allclients=self.main.classview.get_multiple()
            
        elif self.main.listview.isactive() and self.main.config.GetVar("selectedhosts") == 1:
            allclients=self.main.listview.getmultiple()
            if len(allclients) == 0:
                allclients=self.main.localdata.allclients
        else:
            # get all clients connected
            allclients=self.main.localdata.allclients

        if len(allclients) == 0:
            shared.info_msg ( _("No clients connected, press refresh button.") )
            return False
        
        self.allclients=allclients
        
        self.connected_users=[]
        self.connected_users_txt=""
        self.connected_users_txt_all=""
        self.allclients_txt=""
        self.newallclients=[]
        self.newallclients_txt=""
        self.allclients_logged=[]
        self.allclients_logged_txt=""
        counter=1
        counter_all=1
        for client in allclients:
            self.allclients_txt+="\n %s" %(client)
            self.main.localdata.newhost(client)
            if self.main.localdata.IsLogged(client):
                username=self.main.localdata.GetUsernameAndHost(client)
                if username.find(":") != -1:
                    usern, ip = username.split(":")
                    self.connected_users_txt+="%s, " %(usern)
                    self.connected_users_txt_all+="%s, " %(usern)
                else:
                    self.connected_users_txt+="%s, " %(username)
                    self.connected_users_txt_all+="%s, " %(username)
                self.connected_users.append(username)
                if counter % 4 == 0:
                    self.connected_users_txt+="\n"
                if counter_all % 4 == 0:
                    self.connected_users_txt_all+="\n"
                counter=int(counter+1)
                counter_all=int(counter_all+1)
                self.newallclients.append(client)
                self.newallclients_txt+="\n %s" %(client)
                self.allclients_logged.append(client)
                self.allclients_logged_txt+="\n %s" %(client)
            elif not self.main.xmlrpc.IsStandalone(client):
                self.allclients_logged.append(client)
                self.allclients_logged_txt+="\n %s" %(client)
                self.connected_users_txt_all+="%s, " %(client)
                if counter_all % 4 == 0:
                    self.connected_users_txt_all+="\n"
                counter_all=int(counter_all+1)
            else:
                self.connected_users_txt_all+="%s, " %(client)
                if counter_all % 4 == 0:
                    self.connected_users_txt_all+="\n"
                counter_all=int(counter_all+1)

        if self.connected_users_txt[-2:] == "\n": self.connected_users_txt=self.connected_users_txt[:-2]
        if self.connected_users_txt[-2:] == ", ": self.connected_users_txt=self.connected_users_txt[:-2]
        
        if self.connected_users_txt_all[-2:] == "\n": self.connected_users_txt_all=self.connected_users_txt_all[:-2]
        if self.connected_users_txt_all[-2:] == ", ": self.connected_users_txt_all=self.connected_users_txt_all[:-2]
        return True

########################################################################################


    def doaction_onthisclient(self, action, ip):
        # return True if an exec action
        # return False if can not
        # get $DISPLAY
        host, dnum =  os.environ["DISPLAY"].split(':')
        if host == "": return True
        print_debug("doaction_onthisclient() host=%s ip=%s action=%s filteraction=%s" %(host, ip, action, action.split(' ')[0]) )
        # convert to IP
        host=socket.gethostbyname(host)
        print_debug("doaction_onthisclient() comparing %s <=> %s"%(host, socket.gethostbyname(host) ) )
        if int(self.main.config.GetVar("blockactioninthishost")) == 1 and host == socket.gethostbyname(ip):
            print_debug("doaction_onthisclient() ALERT !!! searching for dangerous actions")
            # dangerous actions
            if action.split(' ')[0] in ["poweroff", "reboot", "lockscreen", "restartx", "down-controller"]:
                print_debug("doaction_onthisclient() returning FALSE")
                return False
            print_debug("doaction_onthisclient() no dangerous action")
        print_debug("doaction_onthisclient() no host match")
        return True


    def action_for_clients(self, allclients, action):
        if not allclients or len(allclients) < 1:
            return
        
        print_debug("action_for_clients() allclients='%s' action='%s'"%(allclients, action))
        
        self.main.common.threads_enter("TcosActions::action_for_clients cleaning")
        self.start_action()
        self.main.progressbar.show()
        self.main.common.threads_leave("TcosActions::action_for_clients cleaning")
        
        
        for ip in allclients:
            if not self.doaction_onthisclient(action, ip):
                # show a msg
                print_debug( _("Can't exec this action at '%s' because you are connected at this host!") %ip )
                self.main.common.threads_enter("TcosActions::action_for_clients doing action")
                self.main.write_into_statusbar( _("Can't exec this action at '%s' because you are connected at this host!") %ip )
                self.main.common.threads_leave("TcosActions::action_for_clients doing action")
                continue
            
            
            percent=float( allclients.index(ip)/len(allclients) )
            
            print_debug ( "doing %s in %s, percent complete=%f"\
                             %(action, ip, percent) )
            
            mydict={}
            mydict["action"]=action
            mydict["ip"]=ip
            self.main.common.threads_enter("TcosActions::action_for_clients doing action")
            self.main.actions.set_progressbar( _("Doing action \"%(action)s\" in %(ip)s...") %mydict , percent )
            self.main.common.threads_leave("TcosActions::action_for_clients doing action")

            if not self.main.xmlrpc.connected:
                print_debug("action_for_clients() xmlrpc not connected")
                continue
            
            try:
                # call new IP
                self.main.xmlrpc.newhost(ip)
                # overwrite real_action in your extension
                self.real_action(ip, action)
                ########################################
            except Exception, err:
                print_debug ( "action_for_clients() error while exec '%s' in %s error: %s" %(action, ip, err) )
                pass
        
            self.main.common.threads_enter("TcosActions::action_for_clients END client")
            self.main.actions.set_progressbar( _("Done action \"%(action)s\" in %(ip)s") %mydict , 1 )
            self.main.common.threads_leave("TcosActions::action_for_clients END")
            #sleep(shared.wait_between_many_host)
        
        self.main.common.threads_enter("TcosActions::action_for_clients END all")
        self.finish_action()
        self.main.progressbar.hide()
        self.main.common.threads_leave("TcosActions::action_for_clients END all")
        return

    def change_lockscreen(self, ip):
        """
        change lockscreen icon
           status=True   icon=locked.png
           status=False  icon=unlocked.png
        """
        #self.main.localdata.newhost(ip)
        status_net=self.main.localdata.IsBlockedNet(ip)
        status_screen=self.main.localdata.IsBlocked(ip)
        status_dpms=self.main.xmlrpc.dpms('status', ip)
        print_debug ( "change_lockscreen(%s)=(LOCK)%s,(NET)%s,(DPMS)%s" %(ip, status_screen, status_net, status_dpms) )
        
        locked_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'locked.png')
        locked_net_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'locked_net.png')
        locked_net_screen_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'locked_net_screen.png')
        unlocked_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'unlocked.png')
        dpms_off_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'menu_dpms_off.png')
        dpms_on_image  = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'menu_dpms_on.png')
        
        if status_dpms == 'Off':
            image=dpms_off_image
        elif status_screen and status_net:
            image=locked_net_screen_image
        elif status_screen == False and status_net:
            image=locked_net_image
        #elif status_screen == False and status_net == False and status_dpms == 'On':
        #    image=dpms_on_image
        elif status_screen and status_net == False:
            image=locked_image
        else:
            image=unlocked_image
        
        if self.main.classview.isactive():
            self.main.classview.change_lockscreen(ip, image, status_screen, status_net)
        if self.main.iconview.isactive():
            self.main.iconview.change_lockscreen(ip, image, status_screen, status_net)
        if self.main.listview.isactive():
            self.main.listview.change_lockscreen(ip, image)

    def add_progressbox(self, args, text):
        print_debug("add_progressbox() args=%s, text=%s" %(args, text))
        table=gtk.Table(2, 2, False)
        table.show()
        button=gtk.Button(_("Stop"))
        image = gtk.Image()
        image.set_from_stock (gtk.STOCK_STOP, gtk.ICON_SIZE_BUTTON)
        button.set_image(image)
        button.connect('clicked', self.on_progressbox_click, args, table)
        button.show()
        label=gtk.Label( text )
        label.show()
        table.attach(button, 0, 1, 0, 1, False, False, 0, 0)
        table.attach(label, 1, 2, 0, 1 )
        self.main.progressbox.add(table)
        self.main.progressbox.show()
        self.main.stop_running_actions.append(button)
        print_debug("add_progressbox() widget=%s" %(button))

    def on_progressbox_click(self, widget, args, box):
        #def on_progressbox_click(self, *args):
        raise Error, "TcosExtension on_progressbox_click() not defined"

    def real_action(self, ip, action):
        #def real_action(self, *args):
        raise Error, "TcosExtension real_action() not defined"

    def start_action(self, *args):
        print_debug("start_action() not defined")
        pass

    def finish_action(self, *args):
        print_debug("finish_action() not defined")
        pass


class TcosExtLoader(object):
    def __init__(self, main):
        self.main=main
        self.extensions=None

        import tcosmonitor.extensions as __ext__
        self.extensions=__ext__
        
        #print_debug ("TcosExtLoader::__init__()%s" %self.extensions )
        
        for _ext in self.extensions.__all__:
            obj=getattr( self.extensions, _ext )
            if hasattr(obj, "__extclass__"):
                print_debug( "TcosExtLoader::__init__() registering extension %s"%_ext )
                tmp=obj.__extclass__(self.main)
                tmp.register()
            else:
                raise Error, "Extension '%s' don't have defined __extclass__ attribute" % _ext
        return



if __name__ == '__main__':
    shared.debug=True
    app=TcosExtLoader(None)
