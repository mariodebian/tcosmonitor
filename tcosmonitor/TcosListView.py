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

import sys
import gtk
from gettext import gettext as _


import tcosmonitor.shared

COL_HOST, COL_IP, COL_USERNAME, COL_ACTIVE, COL_LOGGED, COL_BLOCKED, COL_PROCESS, COL_TIME, COL_SEL, COL_SEL_ST = range(10)


# constant to font sizes
PANGO_SCALE=1024


def print_debug(txt):
    if tcosmonitor.shared.debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)

class TcosListView(object):

    def __init__(self, main):
        print_debug("__init__()")
        self.main=main
        self.ui=self.main.ui
        
        
        self.main.updating=True
        self.searching=False  # boolean True thread running False not running
        
        # define as None and register with info extension
        self.populate_datatxt=None
        
        self.model=gtk.ListStore(str, str, str, gtk.gdk.Pixbuf, gtk.gdk.Pixbuf, gtk.gdk.Pixbuf, str, str, bool,bool)
        
        self.main.tabla = self.ui.get_object('hostlist')
        self.main.tabla.set_model (self.model)

        cell1 = gtk.CellRendererText ()
        column1 = gtk.TreeViewColumn (_("Hostname"), cell1, text = COL_HOST)
        column1.set_resizable (True)
        column1.set_sort_column_id(COL_HOST)
        self.main.tabla.append_column (column1)
        
        cell2 = gtk.CellRendererText ()
        column2 = gtk.TreeViewColumn (_("IP address"), cell2, text = COL_IP)
        column2.set_resizable (True)
        column2.set_sort_column_id(COL_IP)
        self.main.tabla.append_column (column2)

        cell3 = gtk.CellRendererText ()
        column3 = gtk.TreeViewColumn (_("Username"), cell3, text = COL_USERNAME)
        column3.set_resizable (True)
        column3.set_sort_column_id(COL_USERNAME)
        self.main.tabla.append_column (column3)

        cell4 = gtk.CellRendererPixbuf()
        column4 = gtk.TreeViewColumn (_("Active"), cell4, pixbuf = COL_ACTIVE)
        #column4.set_sort_column_id(COL_ACTIVE)
        self.main.tabla.append_column (column4)

        cell5 = gtk.CellRendererPixbuf()
        column5 = gtk.TreeViewColumn (_("Logged"), cell5, pixbuf = COL_LOGGED)
        #column5.set_sort_column_id(COL_LOGGED)
        self.main.tabla.append_column (column5)

        cell6 = gtk.CellRendererPixbuf()
        column6 = gtk.TreeViewColumn (_("Screen Blocked"), cell6, pixbuf = COL_BLOCKED)
        #column6.set_sort_column_id(COL_BLOCKED)
        self.main.tabla.append_column (column6)

        cell7 = gtk.CellRendererText ()
        column7 = gtk.TreeViewColumn (_("Num of process"), cell7, text = COL_PROCESS)
        column7.set_resizable (True)
        column7.set_sort_column_id(COL_PROCESS)
        self.main.tabla.append_column (column7)
        
        cell8 = gtk.CellRendererText ()
        column8 = gtk.TreeViewColumn (_("Time log in"), cell8, text = COL_TIME)
        column8.set_resizable (True)
        column8.set_sort_column_id(COL_TIME)
        self.main.tabla.append_column (column8)
        
        if self.main.config.GetVar("selectedhosts") == 1:
            cell9 = gtk.CellRendererToggle ()
            cell9.connect('toggled', self.on_sel_click, self.model, COL_SEL_ST)
            #column9 = gtk.TreeViewColumn(_("Sel"), cell9, active=COL_SEL_ST, activatable=1) # activatable make warnings , not needed
            column9 = gtk.TreeViewColumn(_("Sel"), cell9, active=COL_SEL_ST)
            self.main.tabla.append_column (column9)

        # print rows in alternate colors if theme allow
        self.main.tabla.set_rules_hint(True)
        
        self.main.tabla_file = self.main.tabla.get_selection()
        self.main.tabla_file.connect("changed", self.on_hostlist_click)
        # allow to work right click
        self.main.tabla.connect_object("button_press_event", self.on_hostlist_event, self.main.menu)
        return

    def on_hostlist_click(self, hostlist):
        if self.main.worker_running:
            return
        
        if not self.populate_datatxt:
            print_debug ("on_hostlist_click() self.populate_datatxt() NOT DEFINED")
            return
        
        self.main.progressbar.hide()
        (model, iter) = hostlist.get_selected()
        if not iter:
            return
        self.main.selected_host=model.get_value(iter,COL_HOST)
        self.main.selected_ip=model.get_value(iter, COL_IP)
        
        print_debug ( "on_hostlist_clic() selectedhost=%s selectedip=%s" \
            %(self.main.selected_host, self.main.selected_ip) )
            
        # call to read remote info
        #self.main.localdata.newhost(self.main.selected_ip)
        self.main.xmlrpc.newhost(self.main.selected_ip)
        self.main.xmlrpc.ip=self.main.selected_ip
        if not self.main.xmlrpc.isPortListening(self.main.selected_ip, self.main.xmlrpc.lastport):
            print_debug ( "on_host_list_click() XMLRPC not running in %s" %(self.main.selected_ip) )
            self.main.write_into_statusbar ( _("Error connecting to tcosxmlrpc in %s") %(self.main.selected_ip) )
            return
        
        print_debug ( "on_host_list_click() AUTH OK" )
        
        self.main.write_into_statusbar ( "" )
        print_debug ( "on_hostlist_click() callig worker to populate in Thread" )
        
        
        self.main.worker=tcosmonitor.shared.Workers( self.main,\
                     target=self.populate_datatxt, args=([self.main.selected_ip]) ).start()
        
        return


    def on_hostlist_event(self, widget, event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = self.main.tabla.get_path_at_pos(x, y)
            if pthinfo is not None:
                
                path, col, cellx, celly = pthinfo
                #generate menu
                self.main.menus.RightClickMenuOne( path )
                
                self.main.tabla.grab_focus()
                self.main.tabla.set_cursor( path, col, 0)
                self.main.menu.popup( None, None, None, event.button, time)
                return 1
            else:
                self.main.menus.RightClickMenuAll()
                self.main.allmenu.popup( None, None, None, event.button, time)
                print_debug ( "on_hostlist_event() NO row selected" )
                return

    def on_sel_click(self, cell, path, model, col=0):
        # reverse status of sel row (saved in COL_SEL_ST)
        iter = model.get_iter(path)
        self.model.set_value(iter, col, not model[path][col])
        print_debug("on_sel_click() ip=%s status=%s" %(model[path][COL_IP], model[path][col]))
        return True

    def isenabled(self):
        """
        return True if only configuration enable IconView
        prevent to work if ClassView is hidden
        """
        if self.main.config.GetVar("listmode") == 'list' or \
             self.main.config.GetVar("listmode") == 'both':
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
        if self.main.viewtabs.get_current_page() != 0:
            return False
        return True

    def clear(self):
        self.model.clear()

    def generate_file(self, data):
        self.iter = self.model.append (None)
        self.model.set_value (self.iter, COL_HOST, data['hostname'] )
        self.model.set_value (self.iter, COL_IP, data['host'] )
        self.model.set_value (self.iter, COL_USERNAME, data['username'] )
        self.model.set_value (self.iter, COL_ACTIVE, data['image_active'] )
        self.model.set_value (self.iter, COL_LOGGED, data['image_logged'] )
        self.model.set_value (self.iter, COL_BLOCKED, data['image_blocked'] )
        self.model.set_value (self.iter, COL_PROCESS, data['num_process'] )
        self.model.set_value (self.iter, COL_TIME, data['time_logged'] )

    def getmultiple(self):
        allclients=[]
        #model=self.main.tabla.get_model()
        rows = []
        self.model.foreach(lambda model, path, iter: rows.append(path))
        for host in rows:
            iter=self.model.get_iter(host)
            if self.model.get_value(iter, COL_SEL_ST):
                allclients.append(self.model.get_value(iter, COL_IP))
        return allclients

    def get_selected(self):
        (model, iter) = self.main.tabla.get_selection().get_selected()
        if iter == None:
            print_debug( "get_selected() not selected thin client !!!" )
            return
        return model.get_value(iter, COL_IP)

    def get_host(self, ip):
        (model, iter) = self.main.tabla.get_selection().get_selected()
        if iter == None:
            print_debug( "get_selected() not selected thin client !!!" )
            return
        return model.get_value(iter, COL_HOST)

    def change_lockscreen(self, ip, image):
        self.model.foreach(self.__lockscreen_changer, [ip, image])
        
        
    def __lockscreen_changer(self, model, path, iter, args):
        ip, image = args
        # change image if ip is the same.
        if model.get_value(iter, COL_IP) == ip:
            model.set_value(iter, COL_BLOCKED, image)

    def refresh_client_info(self, ip, data):
        self.model.foreach(self.__refresh_client_info, [ip, data] )

    def __refresh_client_info(self, model, path, iter, args):
        ip, data = args
        print_debug ( "__refresh_client_info()  ip=%s model_ip=%s" %(ip, model.get_value(iter, COL_IP)) )
        # update data if ip is the same.
        if model.get_value(iter, COL_IP) == ip:
            #self.set_client_data(ip, model, iter)
            model.set_value (iter, COL_HOST, data['hostname'] )
            model.set_value (iter, COL_IP, data['ip'] )
            model.set_value (iter, COL_USERNAME, data['username'] )
            model.set_value (iter, COL_ACTIVE, data['image_active'] )
            model.set_value (iter, COL_LOGGED, data['image_logged'] )
            model.set_value (iter, COL_BLOCKED, data['image_blocked'] )
            model.set_value (iter, COL_PROCESS, data['num_process'] )
            model.set_value (iter, COL_TIME, data['time_logged'] )

