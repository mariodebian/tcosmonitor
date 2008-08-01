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

class TcosClassView(object):
    def __init__(self,main):
        print_debug("__init__()")
        self.main=main
        self.ui=self.main.ui
        self.hosts={}
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
        
        self.classview=self.ui.get_widget('classview')
        self.classeventbox=self.ui.get_widget('classeventbox')
        self.classview.drag_dest_set(gtk.DEST_DEFAULT_MOTION |
                                  gtk.DEST_DEFAULT_HIGHLIGHT |
                                  gtk.DEST_DEFAULT_DROP,
                                  [], gtk.gdk.ACTION_MOVE)
        self.classview.drag_dest_set(0, [], 0)
        self.classview.connect('drag_motion', self.motion_cb)
        self.classview.connect('drag_drop', self.on_drag_data_received)
        self.classeventbox.connect("button_press_event", self.on_classview_click)
        #self.classeventbox.connect("size-allocate", self.get_max_pos)
        
        self.oldpos={}
        #self.classview.set_size_request(200, 200)
        self.initialX=10
        self.initialY=10
        self.position=[10,10]
        self.iconsize=[115,115]
        
        # gtk.Frame don't support changing background color (default gray) use glade eventbox
        self.classeventbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
        self.loadpos()

    def get_max_pos(self, *args):
        x, y, width, height = self.classeventbox.get_allocation()
        #print_debug("get_max_pos() width=%s height=%s"%(width, height))
        return [width, height]


    def isenabled(self):
        """
        return True if only configuration enable IconView
        prevent to work if ClassView is hidden
        """
        if self.main.config.GetVar("listmode") == 'icons' or \
             self.main.config.GetVar("listmode") == 'both' or \
             self.main.config.GetVar("listmode") == 'class':
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
        if self.main.viewtabs.get_current_page() != 2:
            return False
        print_debug("isactive() ClassView Mode active")
        return True

    def set_selected(self, ip):
        self.__selected_icon=ip

    def get_selected(self):
        return self.__selected_icon

    def get_host(self, ip):
        if self.hosts.has_key(ip):
            return self.hosts[ip]['hostname']

    def __increment_position(self):
        self.position[0]=self.position[0]+self.iconsize[0]
        #self.position[1]+=50
        print_debug("__increment_position()  position=%s"%(self.position))

    def savepos(self, widget, action):
        if action == "reset":
            self.oldpos={}
            self.main.config.SetVar("positions", "")
            self.main.config.SaveToFile()
            print_debug("savepos() reset to %s"%self.oldpos)
            return
        for w in self.classview.get_children():
            x, y, width, height = w.get_allocation()
            ip=[]
            for c in w.get_children():
                c.get_model().foreach(lambda model, path, iter: ip.append(model.get_value(iter,1)) )
            print_debug("clean() ### POSITION ### x=%s y=%s width=%s height=%s ip=%s"%(x, y, width, height, ip))
            self.oldpos[ip[0]]=[x,y]
        print_debug("savepos() self.oldpos=%s"%self.oldpos)
        txt=""
        for ip in self.oldpos:
            txt+="%s:%s:%s,"%(ip, self.oldpos[ip][0], self.oldpos[ip][1] )
        # remove last coma
        txt=txt[:-1]
        print_debug("savepos() txt=%s"%txt)
        self.main.config.SetVar("positions", txt)
        self.main.config.SaveToFile()

    def loadpos(self):
        print_debug("loadpos()")
        txt=self.main.config.GetVar("positions")
        if txt == "": return
        self.oldpos={}
        a=txt.split(',')
        for host in a:
            if len(host) < 1: continue
            h=host.split(':')
            self.oldpos[h[0]]=[int(h[1]),int(h[2])]
        print_debug("loadpos() self.oldpos=%s"%self.oldpos)

    def clear(self):
        for w in self.classview.get_children():
            w.destroy()
        self.position=[self.initialX,self.initialY]
        print_debug("clear() restore position to %s"%(self.position))


    def generate_icon(self, data):
        print_debug("generate_icon() data=%s"%data)
        
        iconview=gtk.IconView()
        model = gtk.ListStore(str, str ,gtk.gdk.Pixbuf)
        if data['standalone']:
            pixbuff = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'host_standalone.png')
        else:
            pixbuff = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'host_tcos.png')
        iconview.set_model(model)
        iconview.set_text_column(0)
        iconview.set_pixbuf_column(2)
        iconview.props.has_tooltip = True
        model.append([data['hostname'], data['ip'], pixbuff])
        
        iconview.show()
        
        button = gtk.Button()
        button.set_relief(gtk.RELIEF_NONE)
        button.add(iconview)
        button.drag_source_set(gtk.gdk.BUTTON1_MASK, [], gtk.gdk.ACTION_COPY)
        button.connect("button_press_event", self.on_iconview_click, data['ip'])
        button.show_all()
        
        if self.oldpos.has_key(data['ip']):
            # we have and old possition
            print_debug("generate_icon() found old position => %s"%self.oldpos[data['ip']])
            self.classview.put(button, self.oldpos[data['ip']][0], self.oldpos[data['ip']][1] )
        else:
            self.classview.put(button, self.position[0], self.position[1])
            self.__increment_position()
        self.hosts[data['ip']]=data
        
    def on_drag_data_received(self, widget, context, x, y, time):
        button=context.get_source_widget()
        bx, by, width, height = button.get_allocation()
        #print_debug("%s" %context.drag_get_data())
        #print_debug("on_drag_data_received() ### TARGET POS   ### x=%s y=%s"%(x, y))
        #print_debug("on_drag_data_received() ### OLD POSITION ### x=%s y=%s width=%s height=%s"%(bx, by, width, height))
        #print_debug("on_drag_data_received() ### NEW POSITION ### x=%s y=%s "%(x-(width/2), y-(height/2)))
        newx=x-(width/2)
        newy=y-(height/2)
        maxpos=self.get_max_pos()
        if newx < 0: newx=10
        if newy < 0: newy=10
        print_debug("on_drag_data_received() newx=%s newy=%s maxpos[0]=%s maxpos[1]=%s"%(newx, newy, maxpos[0], maxpos[1]))
        if newx > maxpos[0]:
            print_debug("on_drag_data_received() newx=%s > maxpos[0]=%s or negative"%(newx, maxpos[0]))
            return
        if newy > maxpos[1]:
            print_debug("on_drag_data_received() newy=%s > maxpos[1]=%s or negative"%(newy, maxpos[1]))
            return
        # FIXME search for other host to not put over
        self.classview.move(button, newx, newy)

    def motion_cb(self, widget, context, x, y, time):
        context.drag_status(gtk.gdk.ACTION_MOVE, time)
        return True

    def on_iconview_click(self, iv, event, ip):
        if event.button == 3:
            print_debug("on_iconview_click() ip=%s" %(ip))
            self.main.actions.RightClickMenuOne( None , None, ip)
            self.main.menu.popup( None, None, None, event.button, event.time)
            self.set_selected(ip)
            return True

    def on_classview_click(self, iv, event):
        if event.button == 3:
            # need to remake allmenu (for title selected|all )
            self.main.actions.RightClickMenuAll()
            self.main.allmenu.popup( None, None, None, event.button, event.time)
            self.set_selected(None)
            return



