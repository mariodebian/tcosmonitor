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

from time import time
import gobject
import gtk
from gettext import gettext as _
import os
import socket


import shared
from threading import Thread

def print_debug(txt):
    if shared.debug:
        print "%s::%s" % (__name__, txt)

def crono(start, txt):
    print_debug ("crono(), %s get %f seconds" %(txt, (time() - start)) )
    return



class TcosActions:
    def __init__(self, main):
        print_debug ( "__init__()" )
        self.main=main
        self.button_action_audio=None
        self.button_action_chat=None
        self.button_action_list=None
        self.button_action_video=None
        self.button_action_send=None
        self.button_action_exe=None
        self.button_action_text=None
        #self.model=self.main.init.model
        #self.main.progressstop_args={}

    def on_allhostbutton_click(self, widget):
        print_debug("on_allhostbutton_click() ....")
        event = gtk.gdk.Event(gtk.gdk.BUTTON_PRESS)
        self.main.menus.RightClickMenuAll()
        self.main.allmenu.popup( None, None, None, event.button, event.time)
        return True

    def on_preferencesbutton_click(self, widget):
        self.main.pref.show()
    
    def on_aboutbutton_click(self, widget):
        #self.main.about.show()
        self.main.abouttcos.show()
    
    def on_fullscreenbutton_click(self, widget):
        if self.main.is_fullscreen:
            self.main.mainwindow.unfullscreen()
            self.main.is_fullscreen=False
            self.main.fullscreenbutton.set_stock_id("gtk-fullscreen")
        else:
            self.main.mainwindow.fullscreen()
            self.main.is_fullscreen=True
            self.main.fullscreenbutton.set_stock_id("gtk-leave-fullscreen")
    
    def on_progressbutton_click(self, widget):
        print_debug( "on_progressbutton_click()" )
        
        if not self.main.worker.is_stoped():
            self.main.worker.stop()
            self.main.progressbutton.hide()

    
    def on_refreshbutton_click(self, widget):
        if self.main.config.GetVar("xmlrpc_username") == "" or self.main.config.GetVar("xmlrpc_password") == "":
            return
        self.main.write_into_statusbar ( _("Searching for connected hosts...") )
        
        # clear cached ips and ports
        self.main.xmlrpc.resethosts()
        self.datatxt = self.main.datatxt
        # clear datatxt if len allclients is 0
        self.datatxt.clean()
        
        if self.main.config.GetVar("scan_network_method") == "ping" or self.main.config.GetVar("scan_network_method") == "static":
            # clean icons and files
            self.main.listview.clear()
            self.main.iconview.clear()
            self.main.classview.clear()
            allclients=self.main.localdata.GetAllClients(self.main.config.GetVar("scan_network_method"))
            # ping will call populate_hostlist when finish
            return
        else:
            # clean icons and files
            self.main.listview.clear()
            self.main.iconview.clear()
            self.main.classview.clear()
            allclients=self.main.localdata.GetAllClients(self.main.config.GetVar("scan_network_method"))
            if len(allclients) == 0:
                self.main.write_into_statusbar ( _("Not connected hosts found.") )
                return
            self.main.write_into_statusbar ( _("Found %d hosts" ) %len(allclients) )
            # populate_list in a thread
            self.main.worker=shared.Workers(self.main, self.populate_hostlist, [allclients] )
            self.main.worker.start()
            return
    
        
    def on_searchbutton_click(self, widget):
        if self.main.config.GetVar("xmlrpc_username") == "" or self.main.config.GetVar("xmlrpc_password") == "":
            return
        print_debug ( "on_searchbutton_click()" )
        self.main.search_host(widget)
    
    def on_donatebutton_click(self, widget):
        self.main.donatewindow.show()
    
    def on_donatewindow_close(self, *args):
        notshowagain=self.main.donateshowagain.get_active()
        if notshowagain:
            self.main.config.SetVar("show_donate", "0")
            self.main.config.SaveToFile()
        self.main.donatewindow.hide()
        return True
    
    def on_donateurl_click(self, *args):
        url=self.main.donateurllabel.get_text()
        self.main.common.exe_cmd("x-www-browser %s"%url, verbose=0, background=True)
    
    def on_weburl_click(self, *args):
        self.main.common.exe_cmd("x-www-browser %s"%shared.website, verbose=0, background=True)

    def on_abouttcos_close(self, *args):
        self.main.abouttcos.hide()
        return True
    
    def on_abouttcos_donatecheck_change(self, *args):
        notshowagain=self.main.abouttcos_donatecheck.get_active()
        if notshowagain:
            self.main.config.SetVar("show_donate", "0")
            self.main.config.SaveToFile()
        else:
            self.main.config.SetVar("show_donate", "1")
            self.main.config.SaveToFile()
    ############################################################################

    def populate_host_list(self):
        #allclients=self.main.localdata.GetAllClients( self.main.config.GetVar("scan_network_method") )
        #Thread( target=self.populate_hostlist, args=([allclients]) ).start()
        # clear cached ips and ports
        self.main.xmlrpc.resethosts()
        self.datatxt = self.main.datatxt
        # clear datatxt if len allclients is 0
        self.datatxt.clean()

        self.main.write_into_statusbar ( _("Searching for connected hosts...") )
        
        if self.main.config.GetVar("scan_network_method") == "ping" or self.main.config.GetVar("scan_network_method") == "static":
            # clean icons and files
            self.main.listview.clear()
            self.main.iconview.clear()
            self.main.classview.clear()
            allclients=self.main.localdata.GetAllClients(self.main.config.GetVar("scan_network_method"))
            self.main.refreshbutton.set_sensitive(True)
            return False
            # ping will call populate_hostlist when finish
        else:
            # clean icons and files
            self.main.listview.clear()
            self.main.iconview.clear()
            self.main.classview.clear()
            allclients=self.main.localdata.GetAllClients(self.main.config.GetVar("scan_network_method"))
            if len(allclients) != 0:
                self.main.write_into_statusbar ( _("Found %d hosts" ) %len(allclients) )
                # populate_list in a thread
                self.main.worker=shared.Workers(self.main, self.populate_hostlist, [allclients] )
                self.main.worker.start()
                return False
            self.main.write_into_statusbar ( _("Not connected hosts found.") )
            self.main.refreshbutton.set_sensitive(True)

        print_debug ( "POPULATE_HOST_LIST() returning %s" %(self.main.updating) )
        #return self.main.updating
        return False

    def set_progressbar(self, txt, number, show_percent=True):
        percent=int(number*100)
        if show_percent:
            self.main.progressbar.set_text("%s (%d %%)" %(txt, percent))
        else:
            self.main.progressbar.set_text("%s" %(txt))
        self.main.progressbar.set_fraction(number)
    
    def update_progressbar(self, number):
        number=float(number)
        if number > 1:
            return
        print_debug( "update_progressbar() set number=%f" %(number) )
        self.main.progressbar.set_fraction(number)
    
    def populate_hostlist(self, clients):
        print_debug ( "populate_hostlist() init" )
        start1=time()
        
        # clean list
        print_debug ( "populate_hostlist() clear list and start progressbar!!!" )
        
        self.main.common.threads_enter("TcosActions:populate_hostlist show progressbar")
        
        if shared.disable_textview_on_update and self.main.iconview.isactive():
            self.main.tabla.set_sensitive(True)

        #disable refresh button
        self.main.refreshbutton.set_sensitive(False)
        self.main.progressbar.show()
        self.main.progressbutton.show()
        self.set_progressbar( _("Searching info of hosts..."), 0)
        if self.main.config.GetVar("listmode") == "both":
            self.main.listview.clear()
            self.main.iconview.clear()
            self.main.classview.clear()
        elif self.main.listview.isenabled():
            self.main.listview.clear()
        elif self.main.iconview.isenabled():
            self.main.iconview.clear()
        elif self.main.classview.isenabled():
            self.main.classview.clear()
        self.main.common.threads_leave("TcosActions:populate_hostlist show progressbar")
        
        inactive_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'inactive.png')
        active_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'active.png')
        active_ssl_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'active_ssl.png')
        
        logged_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'logged.png')
        unlogged_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'unlogged.png')
        
        locked_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'locked.png')
        locked_net_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'locked_net.png')
        locked_net_screen_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'locked_net_screen.png')
        unlocked_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'unlocked.png')
        dpms_off_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'menu_dpms_off.png')
        dpms_on_image  = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'menu_dpms_on.png')
        
        i=0
        for host in clients:
            start2=time()
            try:
                if self.main.worker.is_stoped():
                    print_debug ( "populate_hostlist() WORKER IS STOPPED" )
                    break
            except Exception, err:
                print_debug("populate_hostlist() can't read worker status, error=%s"%err)
            i += 1
            self.main.common.threads_enter("TcosActions:populate_hostlist show connecting")
            self.main.progressbar.show()
            self.set_progressbar( _("Connecting to %s...") %(host), float(i)/float(len(clients)) )
            self.main.common.threads_leave("TcosActions:populate_hostlist show connecting")
            
            
            self.main.localdata.newhost(host)
            self.main.xmlrpc.newhost (host)
            
            data={}
            data['host']=host
            data['ip']=host
            data['standalone']=False
            data['logged']=False
            print_debug("populate_hostlist() => get username")
            data['username']=self.main.localdata.GetUsername(data['ip'])
            
            if shared.dont_show_users_in_group != None:
                if self.main.xmlrpc.IsStandalone(data['ip']):
                    groupexclude=self.main.xmlrpc.GetStandalone("get_exclude", shared.dont_show_users_in_group)
                else:
                    groupexclude=self.main.localdata.isExclude(data['ip'], shared.dont_show_users_in_group)
            
                if groupexclude: 
                    print_debug("Host %s excluded, blacklisted by group" %data['ip'])
                    continue
            
            print_debug("populate_hostlist() => get hostname")
            data['hostname']=self.main.localdata.GetHostname(data['ip'])
            
            if data['username'].startswith('error: tcos-last'):
                data['username']="---"
            
            try:
                print_debug("populate_hostlist() => get num process")
                data['num_process']=self.main.localdata.GetNumProcess(data['ip'])
            except Exception, err:
                print_debug("populate_hostlist() Exception getting num process, error=%s"%err)
                data['num_process']="---"
            
            print_debug("populate_hostlist() => get time logged")
            if self.main.xmlrpc.IsStandalone(data['ip']):
                data['time_logged']=self.main.xmlrpc.GetStandalone("get_time")
                data['standalone']=True
            else:
                data['time_logged']=self.main.localdata.GetTimeLogged(data['ip'])
                data['standalone']=False
            
            if not data['time_logged'] or data['time_logged'] == "" or data['time_logged'].startswith('error: tcos-last'):
                data['time_logged']="---"
            
            print_debug("populate_hostlist() => get active connection")
            if self.main.localdata.IsActive(data['ip']):
                data['active']=True
                if self.main.xmlrpc.sslconnection:
                    data['image_active']=active_ssl_image
                else:
                    data['image_active']=active_image
            else:
                data['image_active']=inactive_image
                data['active']=False
            
            print_debug("populate_hostlist() => get is logged")
            if self.main.localdata.IsLogged(data['ip']):
                data['image_logged']=logged_image
                data['logged']=True
            else:
                data['image_logged']=unlogged_image
                data['logged']=False
            
            print_debug("populate_hostlist() => get is blocked")
            if self.main.localdata.IsBlocked(data['ip']):
                data['blocked_screen']=True
            else:
                data['blocked_screen']=False
            
            print_debug("populate_hostlist() => get is blocked net")
            if self.main.localdata.IsBlockedNet(host, data['username']):
                data['blocked_net']=True
            else:
                data['blocked_net']=False

            print_debug("populate_hostlist() => get status dpms")
            if self.main.xmlrpc.dpms('status', data['ip']) == "Off":
                data['dpms_off']=True
            else:
                data['dpms_off']=False
                
            if data['dpms_off']:
                data['image_blocked']=dpms_off_image
            elif data['blocked_screen'] and data['blocked_net']:
                data['image_blocked']=locked_net_screen_image
            elif data['blocked_screen'] == False and data['blocked_net']:
                data['image_blocked']=locked_net_image
            elif data['blocked_screen'] and data['blocked_net'] == False:
                data['image_blocked']=locked_image
            else:
                data['image_blocked']=unlocked_image  

            if self.main.config.GetVar("listmode") == "both":
                self.main.common.threads_enter("TcosActions:populate_hostlist all generate_icon")
                self.main.listview.generate_file(data)
                self.main.iconview.generate_icon(data)
                self.main.classview.generate_icon(data)
                self.main.common.threads_leave("TcosActions:populate_hostlist all generate_icon")

            elif self.main.listview.isactive():
                self.main.common.threads_enter("TcosActions:populate_hostlist LIST generate_icon")
                self.main.listview.generate_file(data)
                self.main.common.threads_leave("TcosActions:populate_hostlist LIST generate_icon")
            
            elif self.main.iconview.isactive():
                self.main.common.threads_enter("TcosActions:populate_hostlist ICON generate_icon")
                self.main.iconview.generate_icon(data)
                self.main.common.threads_leave("TcosActions:populate_hostlist ICON generate_icon")
            
            elif self.main.classview.isactive():
                self.main.common.threads_enter("TcosActions:populate_hostlist CLASS generate_icon")
                self.main.classview.generate_icon(data)
                self.main.common.threads_leave("TcosActions:populate_hostlist CLASS generate_icon")
            
            
            crono(start2, "populate_host_list(%s)" %(data['ip']) )
        
        self.main.common.threads_enter("TcosActions:populate_hostlist END")
        self.main.progressbar.hide()
        self.main.progressbutton.hide()
        self.main.refreshbutton.set_sensitive(True)
        self.main.progressbutton.set_sensitive(True)
        
        if shared.disable_textview_on_update and self.main.iconview.isactive():
            self.main.tabla.set_sensitive(True)
        
        self.main.common.threads_leave("TcosActions:populate_hostlist END")
        
        try:
            self.main.worker.set_finished()
        except Exception, err:
            print_debug("populate_hostlist() Exception setting worker status, err=%s" %err)
            pass
        crono(start1, "populate_host_list(ALL)" )
        return

    def update_hostlist(self):
        #if self.main.config.GetVar("populate_list_at_startup") == "1":
        if float(self.main.config.GetVar("refresh_interval")) > 0:
            update_every=float(self.main.config.GetVar("refresh_interval"))
            if float(self.main.config.GetVar("refresh_interval")) >= 10:
                update_every=float(2)
            self.main.refreshbutton.set_sensitive(False)
            print_debug ( "update_hostlist() every %f secs" %(update_every) )
            gobject.timeout_add(int(update_every * 1000), self.populate_host_list )
            return

if __name__ == "__main__":
    app=TcosActions(None)
