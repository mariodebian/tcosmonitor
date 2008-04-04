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

from time import time, sleep, localtime
import gobject
import gtk
from gettext import gettext as _
import os,subprocess
import string

import shared

def print_debug(txt):
    if shared.debug:
        print "%s::%s" %(__name__, txt)

class TcosPreferences:

    def __init__(self,main):
        self.main=main
        self.ui=self.main.ui
        
        self.visible_menu_items=[]
        
        # init pref window and buttons
        self.main.pref = self.main.ui.get_widget('prefwindow')            
        self.main.pref.hide()
        self.main.pref.set_icon_from_file(shared.IMG_DIR + 'tcos-icon-32x32.png')
        # dont destroy window
        # http://www.async.com.br/faq/pygtk/index.py?req=show&file=faq10.006.htp
        self.main.pref.connect('delete-event', self.prefwindow_close )
        
        # extensions table
        self.main.extensions_table=self.ui.get_widget('extensions_table')
        
        # buttons
        self.main.pref_ok = self.ui.get_widget('pref_ok_button')
        self.main.pref_ok.connect('clicked', self.on_pref_ok_button_click)
        self.main.pref_cancel = self.ui.get_widget('pref_cancel_button')
        self.main.pref_cancel.connect('clicked', self.on_pref_cancel_button_click)
        
        # make pref widgets
        self.main.pref_spin_update = self.main.ui.get_widget('spin_update')
        self.main.pref_cache_timeout = self.main.ui.get_widget('spin_cache_timeout')
        self.main.pref_actions_timeout = self.main.ui.get_widget('spin_actions_timeout')
        self.main.pref_scrotsize = self.main.ui.get_widget('spin_scrotsize')
        self.main.pref_miniscrotsize = self.main.ui.get_widget('spin_miniscrotsize')
        self.main.pref_xmlrpc_username = self.main.ui.get_widget('xmlrpc_username')
        self.main.pref_xmlrpc_password = self.main.ui.get_widget('xmlrpc_password')
        
        self.main.pref_ssh_remote_username = self.main.ui.get_widget('ssh_remote_username')
        self.main.pref_vlc_method_send = self.main.ui.get_widget('vlc_method_send')
        self.populate_select(self.main.pref_vlc_method_send, shared.vlc_methods_send )
        
        # populate selects (only on startup)
        self.main.combo_network_interfaces = self.main.ui.get_widget('combo_networkinterface') 
        self.populate_select(self.main.combo_network_interfaces, self.main.common.GetAllNetworkInterfaces() )
        
        # scan method
        self.main.pref_combo_scan_method = self.main.ui.get_widget('combo_scanmethod')
        self.populate_select(self.main.pref_combo_scan_method, shared.scan_methods )
        
        # static host list button
        self.main.pref_open_static = self.main.ui.get_widget('button_open_static')
        self.main.pref_open_static.connect('clicked', self.on_button_open_static)
        
        # add signal changed to scan_method to enable/disable button on the fly
        #self.main.pref_combo_scan_method.connect('changed', self.on_scan_method_change)
        
        
        # checkboxes
        self.main.pref_populatelistatstartup = self.main.ui.get_widget('ck_showliststartup')
        self.main.pref_cybermode = self.main.ui.get_widget('ck_cybermode')
        self.main.pref_systemprocess = self.main.ui.get_widget('ck_systemprocess')
        self.main.pref_threadscontrol = self.main.ui.get_widget('ck_threadscontrol')
        self.main.pref_blockactioninthishost = self.main.ui.get_widget('ck_blockactioninthishost')
        self.main.pref_onlyshowtcos = self.main.ui.get_widget('ck_onlyshowtcos')
        self.main.pref_selectedhosts = self.main.ui.get_widget('ck_selectedhosts')
        
        self.main.pref_tcosinfo = self.main.ui.get_widget('ck_tcosinfo')
        self.main.pref_cpuinfo = self.main.ui.get_widget('ck_cpuinfo')
        self.main.pref_kernelmodulesinfo = self.main.ui.get_widget('ck_kernelmodulesinfo')
        self.main.pref_pcibusinfo = self.main.ui.get_widget('ck_pcibusinfo')
        self.main.pref_ramswapinfo = self.main.ui.get_widget('ck_ramswapinfo')
        self.main.pref_processinfo = self.main.ui.get_widget('ck_processinfo')
        self.main.pref_networkinfo = self.main.ui.get_widget('ck_networkinfo')
        self.main.pref_xorginfo = self.main.ui.get_widget('ck_xorginfo')
        self.main.pref_soundserverinfo = self.main.ui.get_widget('ck_soundserverinfo')
        
        # menus show hide
        for menu in shared.preferences_menus:
            setattr(self.main, "pref_" + menu, self.main.ui.get_widget(menu) )


    def SaveSettings(self):
        """
        save settings
        """
        start=time()
        print_debug ( "SaveSettings() INIT" )
        self.main.config.SetVar("xmlrpc_username", "" + self.main.pref_xmlrpc_username.get_text() )
        self.main.config.SetVar("xmlrpc_password", "" + self.main.pref_xmlrpc_password.get_text() )
        
        self.main.config.SetVar("ssh_remote_username", "" + self.main.pref_ssh_remote_username.get_text() )
        
        if self.main.pref_vlc_method_send.get_active() == 0:
            self.main.config.SetVar("vlc_method_send", "ffmpeg-MPEG4")
        elif self.main.pref_vlc_method_send.get_active() == 1:
            self.main.config.SetVar("vlc_method_send", "ffmpeg-MPEG1")
        elif self.main.pref_vlc_method_send.get_active() == 2:
            self.main.config.SetVar("vlc_method_send", "x264-MPEG4")
        elif self.main.pref_vlc_method_send.get_active() == 3:
            self.main.config.SetVar("vlc_method_send", "http-Theora")
        elif self.main.pref_vlc_method_send.get_active() == 4:
            self.main.config.SetVar("vlc_method_send", "http-MPEG1")
        
        self.main.config.SetVar("refresh_interval", float(self.main.pref_spin_update.get_value()) )
        
        self.main.config.SetVar("scrot_size", int(self.main.pref_scrotsize.get_value()) )
        self.main.config.SetVar("miniscrot_size", int(self.main.pref_miniscrotsize.get_value()) )
        
        self.main.config.SetVar("cache_timeout", float(self.main.pref_cache_timeout.get_value()) )
        self.main.config.SetVar("actions_timeout", int(self.main.pref_actions_timeout.get_value()) )
        
        self.main.config.SetVar("tcosmonitorversion", shared.version )
        
        self.read_checkbox(self.main.pref_populatelistatstartup, "populate_list_at_startup")
        self.read_checkbox(self.main.pref_cybermode, "work_as_cyber_mode")
        self.read_checkbox(self.main.pref_systemprocess, "systemprocess")
        self.read_checkbox(self.main.pref_threadscontrol, "threadscontrol")
        self.read_checkbox(self.main.pref_blockactioninthishost, "blockactioninthishost")
        self.read_checkbox(self.main.pref_onlyshowtcos, "onlyshowtcos")
        self.read_checkbox(self.main.pref_selectedhosts, "selectedhosts")
            
        if self.main.pref_combo_scan_method.get_active() == 0:
            self.main.config.SetVar("scan_network_method", "netstat")
        elif self.main.pref_combo_scan_method.get_active() == 1:
             self.main.config.SetVar("scan_network_method", "ping")
        else:
            self.main.config.SetVar("scan_network_method", "static")
        
        self.main.config.SetVar("statichosts", self.main.static.get_static_conf() )
        
        self.read_checkbox(self.main.pref_tcosinfo, "tcosinfo")
        self.read_checkbox(self.main.pref_kernelmodulesinfo, "kernelmodulesinfo")
        self.read_checkbox(self.main.pref_pcibusinfo, "pcibusinfo")
        self.read_checkbox(self.main.pref_ramswapinfo, "ramswapinfo")
        self.read_checkbox(self.main.pref_processinfo, "processinfo")
        self.read_checkbox(self.main.pref_networkinfo, "networkinfo")
        self.read_checkbox(self.main.pref_tcosinfo, "tcosinfo")
        self.read_checkbox(self.main.pref_cpuinfo, "cpuinfo")
        self.read_checkbox(self.main.pref_xorginfo, "xorginfo")
        self.read_checkbox(self.main.pref_soundserverinfo, "soundserverinfo")
                    
        # read all combo values and save text
        self.main.config.SetVar("network_interface", \
                self.read_select_value(self.main.combo_network_interfaces, "network_interface") )
        
        visible_menus=[]
        for menu in shared.preferences_menus:
            pref_name=menu.replace('ck_menu_', '')
            widget=getattr(self.main, "pref_" + menu)
            if widget.get_active():
                visible_menus.append(pref_name)
        # convert array into string separated by comas
        self.main.config.SetVar("visible_menus", ",".join(visible_menus) )
        
        self.main.config.SaveToFile()

    def read_checkbox(self, widget, varname):
        if widget.get_active() == 1:
            print_debug ( "read_checkbox(%s) CHECKED" %(widget.name) )
            self.main.config.SetVar(varname, 1)
        else:
            print_debug ( "read_checkbox(%s) UNCHECKED" %(widget.name) )
            self.main.config.SetVar(varname, 0)
    
    def read_select_value(self, widget, varname):
        selected=-1
        try:
            selected=widget.get_active()
        except:
            print_debug ( "read_select() ERROR reading %s" %(varname) )
        #FIXME ALERT
        model=widget.get_model()
        value=model[selected][0]
        print_debug ( "read_select() reading %s=%s" %(varname, value) )
        return value
  

    def prefwindow_close(self, widget, event):
        print_debug ( "prefwindow_close() closing preferences window" )
        self.main.pref.hide()
        return True

    def on_pref_ok_button_click(self, widget):
        self.SaveSettings()
        # refresh pref widgets
        self.populate_pref()
        print_debug ( "on_pref_ok_button_click() SAVE SETTINGS !!!" )
        self.main.write_into_statusbar ( _("New settings saved.") )
        self.main.pref.hide()
        
    def on_pref_cancel_button_click(self, widget):
        print_debug ( "on_pref_cancel_button_click()" )
        # refresh pref widgets
        self.populate_pref()
        self.main.pref.hide()            

    def on_button_open_static(self, widget):
        print_debug("on_button_open_static()")
        self.main.static.show_static()
        self.main.pref.hide()

    def on_scan_method_change(self, widget):
        if widget.get_active() == 2:
            self.main.pref_open_static.set_sensitive(True)
        else:
            self.main.pref_open_static.set_sensitive(False)
    

    def populate_pref(self):
        # set default for combos
        self.set_active_in_select(self.main.pref_combo_scan_method,\
                         self.main.config.GetVar("scan_network_method"))
        self.set_active_in_select(self.main.combo_network_interfaces,\
                         self.main.config.GetVar("network_interface"))
                         
        #if self.main.config.GetVar("scan_network_method") != "static":
        #    self.main.pref_open_static.set_sensitive(False)
        #else:
        #    self.main.pref_open_static.set_sensitive(True)
        
        # set value of spin
        self.main.pref_spin_update.set_value( float(self.main.config.GetVar("refresh_interval")) )
        self.main.pref_cache_timeout.set_value( float(self.main.config.GetVar("cache_timeout")) )
        self.main.pref_actions_timeout.set_value( float(self.main.config.GetVar("actions_timeout")) )
        self.main.pref_scrotsize.set_value( float(self.main.config.GetVar("scrot_size")) )
        self.main.pref_miniscrotsize.set_value( float(self.main.config.GetVar("miniscrot_size")) )
        
        # set value of text widgets
        self.main.pref_xmlrpc_username.set_text(\
                     self.main.config.GetVar("xmlrpc_username").replace('"', '') )
                     
        self.main.pref_xmlrpc_password.set_text(\
                     self.main.config.GetVar("xmlrpc_password").replace('"', '') )
        
        self.main.pref_ssh_remote_username.set_text(\
                     self.main.config.GetVar("ssh_remote_username").replace('"', '') )
                     
        self.set_active_in_select(self.main.pref_vlc_method_send,\
                         self.main.config.GetVar("vlc_method_send"))
        
        
        # populate checkboxes
        self.populate_checkboxes(self.main.pref_populatelistatstartup, "populate_list_at_startup")
        self.populate_checkboxes(self.main.pref_cybermode, "work_as_cyber_mode")
        self.populate_checkboxes(self.main.pref_systemprocess, "systemprocess")
        self.populate_checkboxes(self.main.pref_threadscontrol, "threadscontrol")
        self.populate_checkboxes(self.main.pref_blockactioninthishost, "blockactioninthishost")
        self.populate_checkboxes(self.main.pref_onlyshowtcos, "onlyshowtcos")
        self.populate_checkboxes(self.main.pref_selectedhosts, "selectedhosts")
        
        self.populate_checkboxes(self.main.pref_tcosinfo, "tcosinfo")
        self.populate_checkboxes(self.main.pref_cpuinfo, "cpuinfo")
        self.populate_checkboxes(self.main.pref_kernelmodulesinfo, "kernelmodulesinfo")
        self.populate_checkboxes(self.main.pref_pcibusinfo, "pcibusinfo")
        self.populate_checkboxes(self.main.pref_ramswapinfo, "ramswapinfo")
        self.populate_checkboxes(self.main.pref_processinfo, "processinfo")
        self.populate_checkboxes(self.main.pref_networkinfo, "networkinfo")
        self.populate_checkboxes(self.main.pref_xorginfo, "xorginfo")
        self.populate_checkboxes(self.main.pref_soundserverinfo, "soundserverinfo")
        
        # menus show hide
        visible_menus=[]
        visible_menu_items=[]
        first_run=False
        
        visible_menus_txt=self.main.config.GetVar("visible_menus")
        if visible_menus_txt != "":
            visible_menus=visible_menus_txt.split(',')
        else:
            first_run=self.main.config.IsNew("visible_menus")
        
        
        for menu in shared.preferences_menus:
            pref_name=menu.replace('ck_menu_', '')
            widget=getattr(self.main, "pref_" + menu)
            if first_run:
                # first run, set defaults
                widget.set_active(shared.preferences_menus[menu][0])
                visible_menu_items.append(menu)
                continue
                
            if pref_name in visible_menus:
                widget.set_active(1)
                visible_menu_items.append(menu)
            else:
                widget.set_active(0)
        
        self.visible_menu_items={"menuone":[], "menuall":[]}
        for item in visible_menu_items:
            self.visible_menu_items["menuone"]+=shared.preferences_menus[item][1]
            self.visible_menu_items["menuall"]+=shared.preferences_menus[item][2]
            
        print_debug("visible_menu_items() %s"%self.visible_menu_items)
        # make menus
        self.main.actions.RightClickMenuOne(None)
        self.main.actions.RightClickMenuAll()
        print_debug("populate_pref() done")
    
    def populate_checkboxes(self, widget, varname):
        checked=self.main.config.GetVar(varname)
        if checked == "":
            checked=1
        checked=int(checked)
        if checked == 1:
            widget.set_active(1)
        else:
            widget.set_active(0)
        return
                  
    def populate_select(self, widget, values):
        valuelist = gtk.ListStore(str)
        for value in values:
            valuelist.append([value.split()[0]])
        widget.set_model(valuelist)
        widget.set_text_column(0)
        model=widget.get_model()
        return
    
    def set_active_in_select(self, widget, default):
        model=widget.get_model()
        for i in range(len(model)):
            if model[i][0] == default:
                print_debug ("set_active_in_select() default is %s, index %d" %( model[i][0] , i ) )
                widget.set_active(i)
        return 

    def add_extension_row(self, args, text):
        # FIXME add checkboxes for every extension
        print_debug("add_extension_file() args=%s, text=%s" %(args, text))
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

