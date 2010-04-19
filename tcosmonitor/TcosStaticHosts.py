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

import sys
import gtk
from gettext import gettext as _
import tcosmonitor.shared
from time import time

COL_IP, COL_MAC= range(2)

# constant to font sizes
PANGO_SCALE=1024

def print_debug(txt):
    if tcosmonitor.shared.debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)

def crono(start, txt):
    print_debug ("crono(), %s get %f seconds" %(txt, (time() - start)) )
    return

class TcosStaticHosts:

    def __init__(self, main):
        print_debug ("__init__ starting")
        self.selected_ip=None
        self.selected_mac=None
        self.mode="add"
        self.data=[]
        self.main=main
        self.ui=self.main.ui
        self.model=gtk.ListStore(str, str)
        
        self.ui = gtk.Builder()
        self.ui.set_translation_domain(tcosmonitor.shared.PACKAGE)
        
        self.ui.add_from_file(tcosmonitor.shared.GLADE_DIR + 'tcosmonitor-staticwindow.ui')
        
        self.main.staticwindow=self.ui.get_object('staticwindow')
        self.main.staticwindow.connect('delete-event', self.staticwindow_close )
        
        self.ui.add_from_file(tcosmonitor.shared.GLADE_DIR + 'tcosmonitor-staticwindownew.ui')
        self.ui.set_translation_domain(tcosmonitor.shared.PACKAGE)
        self.main.staticwindownew=self.ui.get_object('staticwindownew')
        self.main.staticwindownew.connect('delete-event', self.staticwindownew_close )
        
        self.init_statichostlist()
        
        self.main.static_button_cancel=self.ui.get_object('button_static_cancel')
        self.main.static_button_cancel.connect('clicked', self.staticwindow_close)
        
        self.main.static_button_save=self.ui.get_object('button_static_save')
        self.main.static_button_save.connect('clicked', self.staticwindow_save)
        
        self.main.static_button_add=self.ui.get_object('button_static_add')
        self.main.static_button_add.connect('clicked', self.static_add)
        
        self.main.static_button_modify=self.ui.get_object('button_static_modify')
        self.main.static_button_modify.connect('clicked', self.static_modify)
        
        self.main.static_button_delete=self.ui.get_object('button_static_delete')
        self.main.static_button_delete.connect('clicked', self.static_delete)
        
        self.main.static_button_get=self.ui.get_object('button_static_get')
        self.main.static_button_get.connect('clicked', self.static_get)
        
        # static_line buttons
        self.main.static_button_line_cancel=self.ui.get_object('button_static_line_cancel')
        self.main.static_button_line_cancel.connect('clicked', self.staticwindownew_close)
        
        self.main.static_button_line_save=self.ui.get_object('button_static_line_save')
        self.main.static_button_line_save.connect('clicked', self.on_static_new)
        
        # new line
        self.main.static_new_ip=self.ui.get_object('static_new_ip')
        self.main.static_new_mac=self.ui.get_object('static_new_mac')
        
        self.control_buttons(False)
        
        self.init_data(self.main.config.GetVar("statichosts"))
        

    def init_data(self, txt):
        if txt == "": 
            return
        tmp=txt.split("#")
        for host in tmp:
            self.data.append(host.split("|"))
        #remove last empty element
        self.data=self.data[:-1]
        print_debug("init_data() self.data=%s" %self.data)
        self.populate_data(self.data)

    def populate_data(self, data):
        for host in data:
            self.new_line=True
            model=self.main.staticlist.get_model()
            model.foreach(self.line_exists, host)
        
            if self.new_line:
                print_debug("populate_data() adding ip=%s" %host[0])
                self.iter = self.model.append (None)
                self.model.set_value (self.iter, COL_IP, host[0] )
                self.model.set_value (self.iter, COL_MAC, host[1] )

    def line_exists(self, model, path, iter, args):
        ip, mac = args
        # change mac if ip is the same.
        if model.get_value(iter, 0) == ip:
            model.set_value(iter, 1, mac)
            self.new_line=False
        

    def staticwindow_close(self, *args):
        self.main.staticwindow.hide()
        return True
    
    def staticwindownew_close(self, *args):
        self.main.staticwindownew.hide()
        return True

    def init_statichostlist(self):
        print_debug ( "init_statichostlist()" )
        
        self.main.staticlist = self.ui.get_object('staticlist')
        self.main.staticlist.set_model (self.model)

        cell1 = gtk.CellRendererText ()
        column1 = gtk.TreeViewColumn (_("IP address"), cell1, text = COL_IP)
        column1.set_resizable (True)
        column1.set_sort_column_id(COL_IP)
        self.main.staticlist.append_column (column1)
        
        cell2 = gtk.CellRendererText ()
        column2 = gtk.TreeViewColumn (_("MAC address"), cell2, text = COL_MAC)
        column2.set_resizable (True)	
        column2.set_sort_column_id(COL_MAC)
        self.main.staticlist.append_column (column2)
        
        self.table_file = self.main.staticlist.get_selection()
        self.table_file.connect("changed", self.on_static_list_change)
        
        return

    def show_static(self):
        self.main.staticwindow.show()

    def on_static_list_change (self, data):
        (model, iter) = self.main.staticlist.get_selection().get_selected()
        if not iter:
            self.control_buttons(False)
            return
        self.selected_ip=model.get_value(iter,0)
        self.selected_mac=model.get_value(iter, 1)
        print_debug("selected_ip=%s selected_mac=%s" %(self.selected_ip, self.selected_mac))
        self.control_buttons(True)

    def control_buttons(self, seteditable):
        if seteditable:
            self.main.static_button_modify.set_sensitive(True)
            self.main.static_button_delete.set_sensitive(True)
        else:
            self.main.static_button_modify.set_sensitive(False)
            self.main.static_button_delete.set_sensitive(False)

    def static_add(self, widget):
        self.mode="add"
        self.main.static_new_ip.set_sensitive(True)
        self.main.staticwindownew.show()

    def on_static_new(self, widget):
        print_debug("on_static_new()")
        # read ip and mac address
        ip=self.main.static_new_ip.get_text()
        mac=self.main.static_new_mac.get_text()
        
        if self.mode == "add":
            # put into treeview
            self.iter = self.model.append (None)
            self.model.set_value (self.iter, COL_IP, ip )
            self.model.set_value (self.iter, COL_MAC, mac )
        
        if self.mode == "edit":
            model=self.main.staticlist.get_model()
            model.foreach(self.line_changer, [ip, mac])
        
        self.main.static_new_ip.set_text("")
        self.main.static_new_mac.set_text("")
        self.staticwindownew_close()

    def line_changer(self, model, path, iter, args):
        ip, mac = args
        # change mac if ip is the same.
        if model.get_value(iter, 0) == ip:
            model.set_value(iter, 1, mac)
        

    def static_modify(self, widget):
        print_debug("on_static_modify()")
        self.mode="edit"
        self.main.static_new_ip.set_sensitive(False)
        # read ip and mac address
        self.main.static_new_ip.set_text(self.selected_ip)
        self.main.static_new_mac.set_text(self.selected_mac)
        self.main.staticwindownew.show()

    def static_delete(self, widget):
        print_debug("static_delete()")
        (model, iter) = self.main.staticlist.get_selection().get_selected()
        if iter:
            model.remove(iter)

    def line_saver(self, model, path, iter, args):
        ip=model.get_value(iter, 0)
        mac=model.get_value(iter,1)
        self.data.append([ip, mac])
    
    def staticwindow_save(self, widget):
        print_debug("staticwindow_save()")
        # save in conf file
        self.main.preferences.SaveSettings()
        self.staticwindow_close()

    def get_static_conf(self):
        # get items in treeview
        self.data=[]
        model=self.main.staticlist.get_model()
        model.foreach(self.line_saver, [self.data])
        print_debug("get_static_conf() data=%s" %self.data)
        
        # convert in text format
        txt=""
        for host in self.data:
            # host separated with # and ip mac separated with |
            txt+="%s|%s#" %(host[0], host[1])
        print_debug("get_static_conf() txt=%s" %txt)
        return txt



    def static_get(self, widget):
        print_debug ("static_get()")
        if len(self.main.localdata.allclients) < 1:
            # exit if no hosts
            tcosmonitor.shared.error_msg ( _("No hosts found, please click on Refresh button using another method.") )
            return
        
        print_debug ("static_get() allclients=%s"%self.main.localdata.allclients)
        self.data=[]
        # scan hosts and get MAC address
        for host in self.main.localdata.allclients:
            self.main.xmlrpc.newhost(host)
            mac=self.main.xmlrpc.ReadInfo("network_mac")
            if not mac: 
                mac = ""
            self.data.append([host, mac])
            
        print_debug("static_get() data=%s"%self.data)
        self.populate_data(self.data)

        
