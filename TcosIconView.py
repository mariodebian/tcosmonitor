# -*- coding: UTF-8 -*-
##########################################################################
# TcosMonitor writen by MarioDebian <mariodebian@gmail.com>
#
# TcosMonitor version __VERSION__
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


import gobject
import gtk
from gettext import gettext as _
import os,subprocess
import string

import shared

def print_debug(txt):
    if shared.debug:
        print "%s::%s" %(__name__, txt)

class TcosIconView(object):

    def __init__(self,main):
        print_debug("__init__()")
        self.main=main
        self.ui=self.main.ui
        
        self.__selected_icon=None
        self.avalaible_info=[
                    [_("IP"), 'ip' ],
                    [ _("Hostname"), 'hostname' ],
                    [ _("Username"), 'username'],
                    [ _("Logged"), 'logged'],
                    [ _("Time log in"), 'time_logged'],
                    [ _("Screen locked"), 'blocked_screen'],
                    [ _("Network locked"), 'blocked_net'],
                        ]
        self.default_tip = _("Place mouse on any computer to see brief info about it.")
        
        self.icon_tooltips = None
        self.hosts={}
        self.iconview=self.ui.get_widget('iconview')
        self.model = gtk.ListStore(str, str ,gtk.gdk.Pixbuf)
        self.iconview.set_model(self.model)
        self.iconview.set_text_column(0)
        self.iconview.set_pixbuf_column(2)
        
        self.iconview.props.has_tooltip = True
        self.iconview.connect("motion-notify-event", self.on_iconview_event)
        self.iconview.connect("button_press_event", self.on_iconview_click)

    def isenabled(self):
        """
        return True if only configuration enable IconView
        prevent to work if IconView is hidden
        """
        if self.main.config.GetVar("listmode") == 'icons' or self.main.config.GetVar("listmode") == 'both':
            return True
        return False

    def isactive(self):
        """
        Return True if IconView is enabled and is active (We click on it)
        know this getting tabindex of viewtabas widget.
          0 => active list view
          1 => active icon view
        """
        if not self.isenabled:
            return False
        if self.main.viewtabs.get_current_page() != 1:
            return False
        print_debug("isactive() IconView Mode active")
        return True

    def get_multiple(self):
        allhosts=[]
        selected=self.iconview.get_selected_items()
        if len(selected) > 0:
            for sel in selected:
                allhosts.append( self.model[sel][1] )
        print_debug("get_multiple() allhosts=%s"%allhosts)
        return allhosts

    def ismultiple(self):
        if not self.isactive():
            return False
        print_debug("ismultiple() num selected=%s"%len(self.iconview.get_selected_items()))
        if len(self.iconview.get_selected_items()) > 0:
            return True
        else:
            return False

    def clear(self):
        print_debug("clear() clean iconview")
        self.model.clear()
        self.host={}
        self.set_selected(None)

    def set_selected(self, ip):
        self.__selected_icon=ip

    def get_selected(self):
        return self.__selected_icon

    def get_host(self, ip):
        if self.hosts.has_key(ip):
            return self.hosts[ip]['hostname']

    def generate_icon(self, data):
        print_debug("generate_icon() data=%s"%data)
        
        if data['standalone']:
            pixbuf = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'host_standalone.png')
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'host_tcos.png')
        
        if not data['active']:
            pixbuf.saturate_and_pixelate(pixbuf, 0.6, True)
        
        if data['blocked_screen']:
            pixbuf2 = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'locked.png')
            pixbuf2.composite(pixbuf, 0, 0, pixbuf.props.width, pixbuf.props.height, 0, 0, 1.0, 1.0, gtk.gdk.INTERP_HYPER, 255)
        
        self.model.append([data['hostname'], data['ip'], pixbuf])
        self.hosts[data['ip']]=data

    def generate_tooltip(self, ip):
        if not self.hosts.has_key(ip):
            return ""
        data=self.hosts[ip]
        txt=""
        
        for info in self.avalaible_info:
            if data[info[1]] == True:
                value=_("yes")
            elif data[info[1]] == False:
                value=_("no")
            else:
                value=data[info[1]]
            txt+=" %s: %s \n" %(info[0], value)
        # remove last '\n'
        return txt[:-1]

    def on_iconview_event(self, iv, event):
        """Deletes old tooltip and adds new one for new icon."""
        # On mouse move, old tooltip must dissapear.
        self.icon_tooltips = gtk.Tooltips()

        # Adds tip if no buttons are pressed during the move.
        if not event.state:
            pos = iv.get_path_at_pos(int(event.x), int(event.y))
            if pos:
                mod = list(iv.get_model()[pos])
                tip=self.generate_tooltip(mod[1])
            else:
                tip=self.default_tip
            self.icon_tooltips.set_tip(iv, tip)


    def on_iconview_click(self, iv, event):
        if event.button == 3:
            pos = self.iconview.get_path_at_pos(int(event.x), int(event.y))
            if len(self.iconview.get_selected_items()) < 2 and pos:
                #generate menu
                self.main.menus.RightClickMenuOne( pos , self.model)
                
                self.iconview.grab_focus()
                #self.iconview.set_cursor( path, col, 0)
                self.iconview.select_path(pos)
                ip=iv.get_model()[pos][1]
                self.set_selected(ip)
                
                self.main.menu.popup( None, None, None, event.button, event.time)
                return True
            else:
                # need to remake allmenu (for title selected|all )
                self.main.menus.RightClickMenuAll()
                self.main.allmenu.popup( None, None, None, event.button, event.time)
                print_debug ( "on_iconview_click() NO icon selected" )
                self.set_selected(None)
                return


    def change_lockscreen(self, ip, pixbuf2):
        data=self.hosts[ip]
        if data['standalone']:
            pixbuf = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'host_standalone.png')
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'host_tcos.png')
        pixbuf2.composite(pixbuf, 0, 0, pixbuf.props.width, pixbuf.props.height, 0, 0, 1.0, 1.0, gtk.gdk.INTERP_HYPER, 255)
        for m in self.model:
            if m[1] == ip:
                m[2]=pixbuf
                return
        





