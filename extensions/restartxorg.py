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
#from TcosExtensions import TcosExtension, Error
from TcosExtensions import TcosExtension
import gtk

def print_debug(txt):
    if shared.debug:
        print "%s::%s" % ("extensions::restartxorg", txt)
    return


class RestartXorg(TcosExtension):
    def register(self):
        self.main.menus.register_simple( _("Restart X session with new settings"), "menu_newconf.png", 0, self.restartx, "xorg")
        self.main.menus.register_all( _("Restart X session of all clients"),  "menu_newconf.png" , 0, self.restartx_all, "xorg")
        

    def restartx(self, w, ip):
        if not self.get_client():
            return
        # restart xorg with new settings
        # thin client must download again XXX.XXX.XXX.XXX.conf and rebuild xorg.conf
        if self.client_type == "tcos":
            msg=_( "Restart X session of %s with new config?" ) %(ip)
            if shared.ask_msg ( msg ):
                # see xmlrpc/xorg.h, rebuild will download and sed xorg.conf.tpl
                try:
                    self.main.xmlrpc.tc.tcos.xorg("rebuild", "--restartxorg", \
                        self.main.config.GetVar("xmlrpc_username"), \
                        self.main.config.GetVar("xmlrpc_password")  )
                except Exception, err:
                    print_debug("restartx() Exception error %s"%err)
                    pass
                self.refresh_client_info(ip)
        else:
            shared.info_msg( _("%s is not supported to restart Xorg!") %(self.client_type) )

    def restartx_all(self, widget):
        if not self.get_all_clients():
            return
        onlythinclients=[]
        onlythinclients_txt=""
        
        for client in self.allclients:
            if not self.main.xmlrpc.IsStandalone(client):
                onlythinclients.append(client)
                onlythinclients_txt+="\n %s" %(client)
                
        if len(onlythinclients) == 0:
            shared.error_msg( _("No thin clients found.") )
            return
                
        msg=_( _("Do you want to restart X screens (only thin clients):%s?" )%(onlythinclients_txt) )
        if shared.ask_msg ( msg ):
            self.main.worker=shared.Workers(self.main, None, None)
            self.main.worker.set_for_all_action(self.action_for_clients, onlythinclients, "restartx" )


    def real_action(self, ip, action):
        print_debug("real_action() ip=%s action='%s'"%(ip, action) )
        self.main.xmlrpc.Exe(action)


    def refresh_client_info(self, ip):
        print_debug ( "refresh_client_info() updating host data..." )
        
        inactive_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'inactive.png')
        active_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'active.png')
        active_ssl_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'active_ssl.png')
        
        logged_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'logged.png')
        unlogged_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'unlogged.png')
        
        locked_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'locked.png')
        locked_net_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'locked_net.png')
        locked_net_screen_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'locked_net_screen.png')
        unlocked_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'unlocked.png')
        
        # disable cache
        self.main.localdata.cache_timeout=0
        
        data={}
        data['ip']=ip
        print_debug("refresh_client_info() => get username")
        data['username']=self.main.localdata.GetUsername(ip)
        
        print_debug("refresh_client_info() => get hostname")
        data['hostname']=self.main.localdata.GetHostname(ip)
        
        if data['username'].startswith('error: tcos-last'):
            data['username']="---"
            
        try:
            print_debug("refresh_client_info() => get num process")
            data['num_process']=self.main.localdata.GetNumProcess(ip)
        except Exception, err:
            print_debug("refresh_client_info() Exception error=%s"%err)
            data['num_process']="---"
        
        print_debug("refresh_client_info() => get time logged")
        data['time_logged']=self.main.localdata.GetTimeLogged(ip)
            
        if not data['time_logged'] or data['time_logged'] == "" or data['time_logged'].startswith('error: tcos-last'):
            data['time_logged']="---"
        
        print_debug("refresh_client_info() => get active connection")
        if self.main.localdata.IsActive(ip):
            if self.main.xmlrpc.sslconnection:
                data['image_active']=active_ssl_image
            else:
                data['image_active']=active_image
        else:
            data['image_active']=inactive_image
        
        print_debug("refresh_client_info() => get is logged")
        if self.main.localdata.IsLogged(ip):
            data['image_logged']=logged_image
        else:
            data['image_logged']=unlogged_image
        
        print_debug("refresh_client_info() => get is blocked")
        if self.main.localdata.IsBlocked(ip):
            data['blocked_screen']=True
        else:
            data['blocked_screen']=False
        
        print_debug("refresh_client_info() => get is blocked net")
        if self.main.localdata.IsBlockedNet(ip, data['username']):
            data['blocked_net']=True
        else:
            data['blocked_net']=False
                
        if data['blocked_screen'] and data['blocked_net']:
            data['image_blocked']=locked_net_screen_image
        elif data['blocked_screen'] == False and data['blocked_net']:
            data['image_blocked']=locked_net_image
        elif data['blocked_screen'] and data['blocked_net'] == False:
            data['image_blocked']=locked_image
        else:
            data['image_blocked']=unlocked_image
                
        #enable cache again
        self.main.localdata.cache_timeout=shared.cache_timeout
        
        if self.main.classview.isactive():
            self.main.classview.change_lockscreen(ip, data['image_blocked'])
        if self.main.iconview.isactive():
            self.main.iconview.change_lockscreen(ip, data['image_blocked'])
        if self.main.listview.isactive():
            self.main.listview.refresh_client_info(ip, data)



__extclass__=RestartXorg






