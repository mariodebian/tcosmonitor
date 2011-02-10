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
from time import time
import gtk
from gettext import gettext as _

import tcosmonitor.shared

def print_debug(txt):
    if tcosmonitor.shared.debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)

class TcosPreferences:

    def __init__(self, main):
        self.main=main
        #self.ui=self.main.ui
        self.visible_menu_items=[]
        self.ui=gtk.Builder()
        self.ui.set_translation_domain(tcosmonitor.shared.PACKAGE)
        
        # init pref window and buttons
        self.ui.add_from_file(tcosmonitor.shared.GLADE_DIR + 'tcosmonitor-prefwindow.ui')
        self.main.pref = self.ui.get_object('prefwindow')
        self.main.pref.hide()
        self.main.pref.set_icon_from_file(tcosmonitor.shared.IMG_DIR + 'tcos-icon-32x32.png')
        # dont destroy window
        # http://www.async.com.br/faq/pygtk/index.py?req=show&file=faq10.006.htp
        self.main.pref.connect('delete-event', self.prefwindow_close )
        
        # extensions table
        self.main.extensions_table=self.ui.get_object('extensions_table')
        
        # buttons
        self.main.pref_ok = self.ui.get_object('pref_ok_button')
        self.main.pref_ok.connect('clicked', self.on_pref_ok_button_click)
        self.main.pref_cancel = self.ui.get_object('pref_cancel_button')
        self.main.pref_cancel.connect('clicked', self.on_pref_cancel_button_click)
        
        # make pref widgets
        self.main.pref_spin_update = self.ui.get_object('spin_update')
        self.main.pref_cache_timeout = self.ui.get_object('spin_cache_timeout')
        self.main.pref_actions_timeout = self.ui.get_object('spin_actions_timeout')
        self.main.pref_scrotsize = self.ui.get_object('spin_scrotsize')
        self.main.pref_miniscrotsize = self.ui.get_object('spin_miniscrotsize')
        self.main.pref_xmlrpc_username = self.ui.get_object('xmlrpc_username')
        self.main.pref_xmlrpc_password = self.ui.get_object('xmlrpc_password')
        
        self.main.pref_ssh_remote_username = self.ui.get_object('ssh_remote_username')
        self.main.pref_ports_tnc = self.ui.get_object('ports_net_controller')
        self.main.pref_vlc_method_send = self.ui.get_object('vlc_method_send')
        self.populate_select(self.main.pref_vlc_method_send, tcosmonitor.shared.vlc_methods_send )
        
        # populate selects (only on startup)
        self.main.combo_network_interfaces = self.ui.get_object('combo_networkinterface') 
        self.populate_select(self.main.combo_network_interfaces, self.main.common.GetAllNetworkInterfaces() )
        
        # scan method
        self.main.pref_combo_scan_method = self.ui.get_object('combo_scanmethod')
        self.populate_select(self.main.pref_combo_scan_method, tcosmonitor.shared.scan_methods )
        
        # static host list button
        self.main.pref_open_static = self.ui.get_object('button_open_static')
        self.main.pref_open_static.connect('clicked', self.on_button_open_static)
        
        # add signal changed to scan_method to enable/disable button on the fly
        #self.main.pref_combo_scan_method.connect('changed', self.on_scan_method_change)
        
        # listmode method
        self.main.pref_combo_listmode = self.ui.get_object('combo_listmode')
        self.populate_select(self.main.pref_combo_listmode, tcosmonitor.shared.list_modes )
        
        
        # checkboxes
        self.main.pref_populatelistatstartup = self.ui.get_object('ck_showliststartup')
        #self.main.pref_cybermode = self.ui.get_object('ck_cybermode')
        self.main.pref_systemprocess = self.ui.get_object('ck_systemprocess')
        self.main.pref_threadscontrol = self.ui.get_object('ck_threadscontrol')
        self.main.pref_enable_sslxmlrpc = self.ui.get_object('ck_enable_sslxmlrpc')
        self.main.pref_consolekit = self.ui.get_object('ck_consolekit')
        self.main.pref_blockactioninthishost = self.ui.get_object('ck_blockactioninthishost')
        self.main.pref_notshowwhentcosmonitor = self.ui.get_object('ck_notshowwhentcosmonitor')
        self.main.pref_onlyshowtcos = self.ui.get_object('ck_onlyshowtcos')
        self.main.pref_selectedhosts = self.ui.get_object('ck_selectedhosts')
        
        self.main.pref_tcosinfo = self.ui.get_object('ck_tcosinfo')
        self.main.pref_cpuinfo = self.ui.get_object('ck_cpuinfo')
        self.main.pref_kernelmodulesinfo = self.ui.get_object('ck_kernelmodulesinfo')
        self.main.pref_pcibusinfo = self.ui.get_object('ck_pcibusinfo')
        self.main.pref_ramswapinfo = self.ui.get_object('ck_ramswapinfo')
        self.main.pref_processinfo = self.ui.get_object('ck_processinfo')
        self.main.pref_networkinfo = self.ui.get_object('ck_networkinfo')
        self.main.pref_xorginfo = self.ui.get_object('ck_xorginfo')
        self.main.pref_soundserverinfo = self.ui.get_object('ck_soundserverinfo')
        
        self.main.pref_menugroups = self.ui.get_object('ck_menugroups')
        
        # menus show hide
        for menu in tcosmonitor.shared.preferences_menus:
            setattr(self.main, "pref_" + menu, self.ui.get_object(menu) )
            
        for menu in tcosmonitor.shared.button_preferences_menus:
            setattr(self.main, "pref_" + menu, self.ui.get_object(menu) )


    def SaveSettings(self):
        """
        save settings
        """
        start=time()
        print_debug ( "SaveSettings() INIT" )
        self.main.config.SetVar("xmlrpc_username", "" + self.main.pref_xmlrpc_username.get_text() )
        self.main.config.SetVar("xmlrpc_password", "" + self.main.pref_xmlrpc_password.get_text() )
        
        self.main.config.SetVar("ssh_remote_username", "" + self.main.pref_ssh_remote_username.get_text() )
        self.main.config.SetVar("ports_tnc", "" + self.main.pref_ports_tnc.get_text() )
        
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
        
        self.main.config.SetVar("tcosmonitorversion", tcosmonitor.shared.version )
        
        self.read_checkbox(self.main.pref_populatelistatstartup, "populate_list_at_startup")
        #self.read_checkbox(self.main.pref_cybermode, "work_as_cyber_mode")
        self.read_checkbox(self.main.pref_systemprocess, "systemprocess")
        self.read_checkbox(self.main.pref_threadscontrol, "threadscontrol")
        self.read_checkbox(self.main.pref_enable_sslxmlrpc, "enable_sslxmlrpc")
        self.read_checkbox(self.main.pref_consolekit, "consolekit")
        self.read_checkbox(self.main.pref_blockactioninthishost, "blockactioninthishost")
        self.read_checkbox(self.main.pref_notshowwhentcosmonitor, "notshowwhentcosmonitor")
        self.read_checkbox(self.main.pref_onlyshowtcos, "onlyshowtcos")
        self.read_checkbox(self.main.pref_selectedhosts, "selectedhosts")
        
        method=tcosmonitor.shared.scan_methods[self.main.pref_combo_scan_method.get_active()]
        self.main.config.SetVar("scan_network_method", method)
#        if self.main.pref_combo_scan_method.get_active() == 0:
#            self.main.config.SetVar("scan_network_method", "netstat")
#        elif self.main.pref_combo_scan_method.get_active() == 1:
#            self.main.config.SetVar("scan_network_method", "ping")
#        elif self.main.pref_combo_scan_method.get_active() == 2:
#            self.main.config.SetVar("scan_network_method", "nmap")
#        else:
#            self.main.config.SetVar("scan_network_method", "static")
        
        active=self.main.pref_combo_listmode.get_active()
        self.main.config.SetVar("listmode", tcosmonitor.shared.list_modes[active][0])
        
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
        
        self.read_checkbox(self.main.pref_menugroups, "menugroups")
        
        # read all combo values and save text
        self.main.config.SetVar("network_interface", \
                self.read_select_value(self.main.combo_network_interfaces, "network_interface") )
        
        visible_menus=[]
        for menu in tcosmonitor.shared.preferences_menus:
            pref_name=menu.replace('ck_menu_', '')
            widget=getattr(self.main, "pref_" + menu)
            if widget.get_active():
                visible_menus.append("%s:1" %pref_name)
            else:
                visible_menus.append("%s:0" %pref_name)
        # convert array into string separated by comas
        self.main.config.SetVar("visible_menus", ",".join(visible_menus) )
        
        visible_buttons_menus=[]
        for menu in tcosmonitor.shared.button_preferences_menus:
            pref_name=menu.replace('ck_button_menu_', '')
            widget=getattr(self.main, "pref_" + menu)
            if widget.get_active():
                visible_buttons_menus.append("%s:1" %pref_name)
            else:
                visible_buttons_menus.append("%s:0" %pref_name)
        # convert array into string separated by comas
        self.main.config.SetVar("visible_buttons_menus", ",".join(visible_buttons_menus) )

        # reput auth in dbus
        self.main.dbus_action.set_auth( self.main.pref_xmlrpc_username.get_text(), self.main.pref_xmlrpc_password.get_text() )
        
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
        except Exception, err:
            print_debug ( "read_select() ERROR reading %s, error=%s" %(varname, err) )
        #FIXME ALERT
        model=widget.get_model()
        value=model[selected][0]
        print_debug ( "read_select() reading %s=%s" %(varname, value) )
        return value
  

    def prefwindow_close(self, widget, event):
        print_debug ( "prefwindow_close() closing preferences window" )
        self.main.pref.hide()
        return True

    def check_button_pref_menus(self):
        total=0
        for menu in tcosmonitor.shared.button_preferences_menus:
            pref_name=menu.replace('ck_button_menu_', '')
            widget_pref=getattr(self.main, "pref_" + menu)
            if widget_pref.get_active():
                total+=1
        if total > 5:
            tcosmonitor.shared.info_msg(_("You have select more than 5 button menus.\nOnly allowed to select a maximum of 5 buttons."))
            return True
        return False

    def on_pref_ok_button_click(self, widget):
        if self.check_button_pref_menus():
            return
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
        self.set_active_in_select(self.main.pref_combo_scan_method, \
                         self.main.config.GetVar("scan_network_method"))
        self.set_active_in_select(self.main.combo_network_interfaces, \
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
        if self.main.config.use_secrets == False:
            self.main.pref_xmlrpc_username.set_sensitive(True)
            self.main.pref_xmlrpc_password.set_sensitive(True)
            self.main.pref_xmlrpc_username.set_text(\
                        self.main.config.GetVar("xmlrpc_username").replace('"', '') )
                     
            self.main.pref_xmlrpc_password.set_text(\
                        self.main.config.GetVar("xmlrpc_password").replace('"', '') )
        else:
            self.main.pref_xmlrpc_username.set_text("")
            self.main.pref_xmlrpc_password.set_text("")
            self.main.pref_xmlrpc_username.set_sensitive(False)
            self.main.pref_xmlrpc_password.set_sensitive(False)
        
        self.main.pref_ssh_remote_username.set_text(\
                     self.main.config.GetVar("ssh_remote_username").replace('"', '') )
                    
        self.main.pref_ports_tnc.set_text(\
                     self.main.config.GetVar("ports_tnc").replace('"', '') )
                     
        self.set_active_in_select(self.main.pref_vlc_method_send, \
                         self.main.config.GetVar("vlc_method_send"))
        
        self.set_active_in_select(self.main.pref_combo_listmode, \
                        self.main.config.GetVar("listmode") )
        
        # populate checkboxes
        self.populate_checkboxes(self.main.pref_populatelistatstartup, "populate_list_at_startup")
        #self.populate_checkboxes(self.main.pref_cybermode, "work_as_cyber_mode")
        self.populate_checkboxes(self.main.pref_systemprocess, "systemprocess")
        self.populate_checkboxes(self.main.pref_threadscontrol, "threadscontrol")
        self.populate_checkboxes(self.main.pref_enable_sslxmlrpc, "enable_sslxmlrpc")
        self.populate_checkboxes(self.main.pref_consolekit, "consolekit")
        self.populate_checkboxes(self.main.pref_blockactioninthishost, "blockactioninthishost")
        self.populate_checkboxes(self.main.pref_notshowwhentcosmonitor, "notshowwhentcosmonitor")
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
        
        self.populate_checkboxes(self.main.pref_menugroups, "menugroups")
        
        # button menus show hide
        visible_buttons_menus=[]
        visible_buttons_menu_keys={}
        first_run=False
        total=0
        
        visible_buttons_menus_txt=self.main.config.GetVar("visible_buttons_menus")
        if visible_buttons_menus_txt != "":
            print_debug("visible_buttons_menus is not empty")
            visible_buttons_menus=visible_buttons_menus_txt.split(',')
            for item in visible_buttons_menus:
                item = item.split(":")
                if len(item) == 1:
                    visible_buttons_menu_keys[item[0]]="1"
                else:
                    visible_buttons_menu_keys[item[0]]=item[1]                    
        else:
            first_run=self.main.config.IsNew("visible_buttons_menus")
            first_run=True
            print_debug("visible_buttons_menus is empty first_run=%s"%first_run)

        self.main.toolbar2.show()
        for menu in tcosmonitor.shared.button_preferences_menus:
            pref_name=menu.replace('ck_button_menu_', '')
            widget_button=getattr(self.main, "handlebox_" + pref_name)
            widget_pref=getattr(self.main, "pref_" + menu)
            if first_run:
                # first run, set defaults
                if tcosmonitor.shared.button_preferences_menus[menu][0] != False:
                    #widget.set_active(shared.preferences_menus[menu][0])
                    #visible_menu_items.append(menu)
                    #continue
                    #visible_menus.append("%s:1" %pref_name)
                    visible_buttons_menu_keys[pref_name]="1"
                
            if pref_name in visible_buttons_menu_keys.keys():
                if visible_buttons_menu_keys[pref_name] == "1":
                    widget_button.show()
                    widget_pref.set_active(1)
                    total+=1
                elif visible_buttons_menu_keys[pref_name] == "0":
                    widget_button.hide()
                    widget_pref.set_active(0)
            elif pref_name not in visible_buttons_menu_keys.keys() and \
                tcosmonitor.shared.button_preferences_menus[menu][0] != False:
                widget_button.show()
                widget_pref.set_active(1)
                total+=1
            else:
                widget_button.hide()
                widget_pref.set_active(0)
        if total == 0:
            self.main.toolbar2.hide()

        # menus show hide
        visible_menus=[]
        visible_menu_items=[]
        visible_menu_keys={}
        first_run=False
        
        visible_menus_txt=self.main.config.GetVar("visible_menus")
        if visible_menus_txt != "":
            print_debug("visible_menus is not empty")
            visible_menus=visible_menus_txt.split(',')
            for item in visible_menus:
                item = item.split(":")
                if len(item) == 1:
                    visible_menu_keys[item[0]]="1"
                else:
                    visible_menu_keys[item[0]]=item[1]                    
        else:
            first_run=self.main.config.IsNew("visible_menus")
            first_run=True
            print_debug("visible_menus is empty first_run=%s"%first_run)
        
        self.visible_menu_items={"menuone":[], "menuall":[], "names":[]}
        for menu in tcosmonitor.shared.preferences_menus:
            pref_name=menu.replace('ck_menu_', '')
            widget=getattr(self.main, "pref_" + menu)
            if not widget:
                continue
            if first_run:
                # first run, set defaults
                if tcosmonitor.shared.preferences_menus[menu][0] != False:
                    #widget.set_active(shared.preferences_menus[menu][0])
                    #visible_menu_items.append(menu)
                    #continue
                    #visible_menus.append("%s:1" %pref_name)
                    visible_menu_keys[pref_name]="1"
                
            if pref_name in visible_menu_keys.keys():
                if visible_menu_keys[pref_name] == "1":
                    widget.set_active(1)
                    visible_menu_items.append(menu)
                    self.visible_menu_items["names"].append(pref_name)
                elif visible_menu_keys[pref_name] == "0":
                    widget.set_active(0)
            elif pref_name not in visible_menu_keys.keys() and \
                tcosmonitor.shared.preferences_menus[menu][0] != False:
                widget.set_active(1)
                visible_menu_items.append(menu)
                self.visible_menu_items["names"].append(pref_name)
            else:
                widget.set_active(0)
        
        for item in visible_menu_items:
            self.visible_menu_items["menuone"]+=tcosmonitor.shared.preferences_menus[item][1]
            self.visible_menu_items["menuall"]+=tcosmonitor.shared.preferences_menus[item][2]
            
        print_debug("visible_menu_items() %s"%self.visible_menu_items)
        # make menus
        self.main.menus.RightClickMenuOne(None)
        self.main.menus.RightClickMenuAll()
        
        listmode=self.main.config.GetVar("listmode")
        oldtab=self.main.viewtabs.get_current_page()
        
        if listmode == 'list':
            self.main.viewtabs.set_property('show-tabs', False)
            self.main.viewtabs.set_current_page(0)
            self.main.searchbutton.set_sensitive(True)
            self.main.searchtxt.set_sensitive(True)
        elif listmode == 'icons':
            self.main.viewtabs.set_property('show-tabs', False)
            self.main.viewtabs.set_current_page(1)
            self.main.searchbutton.set_sensitive(False)
            self.main.searchtxt.set_sensitive(False)
        elif listmode == 'class':
            self.main.viewtabs.set_property('show-tabs', False)
            self.main.viewtabs.set_current_page(2)
            self.main.searchbutton.set_sensitive(False)
            self.main.searchtxt.set_sensitive(False)
        else:
            self.main.viewtabs.set_property('show-tabs', True)
            self.main.viewtabs.set_current_page(2)
            self.main.searchbutton.set_sensitive(False)
            self.main.searchtxt.set_sensitive(False)
        
        
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
        valuelist = gtk.ListStore(str, str)
        for value in values:
            if isinstance(value, list):
                valuelist.append([value[0], value[1]])
            else:
                valuelist.append([value.split()[0], value.split()[0]])
        widget.set_model(valuelist)
        widget.set_text_column(1)
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
        # FIXME need to add actipon for button click event
        #button.connect('clicked', self.on_progressbox_click, args, table)
        button.show()
        label=gtk.Label( text )
        label.show()
        table.attach(button, 0, 1, 0, 1, False, False, 0, 0)
        table.attach(label, 1, 2, 0, 1 )
        self.main.progressbox.add(table)
        self.main.progressbox.show()

