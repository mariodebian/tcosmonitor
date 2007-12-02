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

import gtk
from gettext import gettext as _
import shared
from time import time
import urllib2
from os import remove, path
from threading import Thread
from subprocess import Popen, PIPE, STDOUT
import popen2

from time import sleep, localtime
import gobject
import string

COL_HOST, COL_IP, COL_USERNAME, COL_ACTIVE, COL_LOGGED, COL_BLOCKED, COL_PROCESS, COL_TIME, COL_SEL, COL_SEL_ST = range(10)


# constant to font sizes
PANGO_SCALE=1024



def print_debug(txt):
    if shared.debug:
        print "%s::%s" %(__name__, txt)

def crono(start, txt):
    print_debug ("crono(), %s get %f seconds" %(txt, (time() - start)) )
    return



class Initialize:
    #drop_targets = [ ( "text/plain", 0, TARGET_TYPE_TEXT ) ]
    
    def __init__(self, main):
        print_debug ( "__init__() starting" )
        self.main=main
        self.ui=self.main.ui
        self.model=gtk.ListStore\
        (str, str, str, gtk.gdk.Pixbuf, gtk.gdk.Pixbuf, gtk.gdk.Pixbuf, str, str, bool,bool)
        
        self.main.updating=True
        
        self.searching=False  # boolean True thread running False not running

        self.main.statusbar=self.ui.get_widget('statusbar')
        
        
        self.ask_mode=None
        
    def get_widget(self, wname):
        widgets = gtk.glade.XML( shared.GLADE_DIR + 'tcosmonitor.glade', wname )
        return widgets.get_widget( wname )
        
    def init_progressbar(self):
        self.main.progressbar=self.ui.get_widget('progressbar')
        self.main.progressbutton=self.ui.get_widget('progressbutton')
        self.main.progressbutton.connect('clicked', self.main.actions.on_progressbutton_click )
        self.main.progressbar.hide()
        self.main.progressbox=self.ui.get_widget('progressbox')
        

        
    def initbuttons(self):
        print_debug ( "initbuttons()" )
        self.main.quitbutton = self.ui.get_widget('quitbutton')
        self.main.quitbutton.connect('clicked', self.main.quitapp)
        
        self.main.preferencesbutton = self.ui.get_widget('preferencesbutton')
        self.main.preferencesbutton.connect('clicked', self.main.actions.on_preferencesbutton_click)
        
        self.main.refreshbutton = self.ui.get_widget('refreshbutton')
        self.main.refreshbutton.connect('clicked', self.main.actions.on_refreshbutton_click)
        
        self.main.fullscreenbutton = self.ui.get_widget('fullscreenbutton')
        self.main.fullscreenbutton.connect('clicked', self.main.actions.on_fullscreenbutton_click)
        
        self.main.allhostbutton = self.ui.get_widget('allhostbutton')
        self.main.allhostbutton.connect('clicked', self.main.actions.on_allhostbutton_click)
        
        self.main.aboutbutton = self.ui.get_widget('aboutbutton')
        self.main.aboutbutton.connect('clicked', self.main.actions.on_aboutbutton_click)
        
        self.main.searchbutton = self.ui.get_widget('searchbutton')
        self.main.searchbutton.connect('clicked', self.main.actions.on_searchbutton_click)
        
        self.main.searchtxt = self.ui.get_widget('searchtxt')
        self.main.searchtxt.connect('activate', self.main.search_host)
        
        
    def initabout(self):
        self.main.about = self.main.ui.get_widget('aboutdialog')
        self.main.about.hide()
        self.main.about.set_icon_from_file(shared.IMG_DIR +\
                                     'tcos-icon-32x32.png')
        self.main.about.set_version(shared.version)
        self.main.about.set_website(shared.website)    
        self.main.about.set_website_label(shared.website_label)
        self.main.about.connect("response", self.on_about_response)
        self.main.about.connect("close", self.on_about_close)
        self.main.about.connect("delete_event", self.on_about_close)
        #self.main.about.about_dialog_set_url_hook(on_url_click)
        #gtk.about_dialog_set_url_hook(self.on_url_click)

    def on_about_response(self, dialog, response, *args):
        #http://www.async.com.br/faq/pygtk/index.py?req=show&file=faq10.013.htp
        if response < 0:
            dialog.hide()
            dialog.emit_stop_by_name('response')
    
    def on_about_close(self, widget, event=None):
        self.main.about.hide()
        return True
    
    def initask(self):
        self.main.ask_ip=None
        
        self.main.ask = self.main.ui.get_widget('askwindow')
        self.main.ask.connect('delete-event', self.main.actions.askwindow_close )
        self.main.ask.set_icon_from_file(shared.IMG_DIR +\
                                         'tcos-icon-32x32.png')
        
        
        self.main.ask_label = self.main.ui.get_widget('txt_asklabel')
        ## arrastrar y soltar
        self.main.ask_fixed = self.main.ui.get_widget('ask_fixed')
        self.main.ask_dragdrop = self.main.ui.get_widget('label99')
        self.main.image_entry = self.main.ui.get_widget('image_askentry')
        self.main.image_entry.drag_dest_set( gtk.DEST_DEFAULT_ALL, [( 'text/uri-list', 0, 2 ),], gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_COPY)
        self.main.image_entry.connect( 'drag_data_received', self.main.actions.on_drag_data_received)
        self.main.ask_fixed.hide()
        self.main.image_entry.hide()
        self.main.ask_dragdrop.hide()
        ## fin arrastrar y soltar
        self.liststore = gtk.ListStore(str)
        for s in shared.appslist:
            self.liststore.append([s])
            
        self.main.ask_entry = self.main.ui.get_widget('txt_askentry')
        self.main.ask_completion = gtk.EntryCompletion()
        self.main.ask_completion.set_model(self.liststore)
        self.main.ask_entry.set_completion(self.main.ask_completion)
        self.main.ask_completion.set_text_column(0)
        
        self.main.ask_completion.connect('match-selected', self.match_cb)
        self.main.ask_entry.connect('activate', self.activate_cb)
        
        self.main.ask_cancel = self.main.ui.get_widget('ask_cancelbutton')
        self.main.ask_exec = self.main.ui.get_widget('ask_exebutton')
        
        # buttons signals
        self.main.ask_exec.connect('clicked', self.main.actions.on_ask_exec_click)
        self.main.ask_cancel.connect('clicked', self.main.actions.on_ask_cancel_click)
        
    
    def match_cb(self, completion, model, iter):
        print_debug ( "match_cb() " )
        print_debug( "%s was selected" %(model[iter][0]) )
        self.main.actions.exe_app_in_client_display(model[iter][0])
        return
    
    def activate_cb(self, entry):
        text = self.main.ask_entry.get_text()
        print_debug ( "activate_cb() text=%s" %(text) )
        
        # append to liststore
        if text:
            if text not in [row[0] for row in self.liststore]:
                self.liststore.append([text])
                #self.main.ask_entry.set_text('')
        
        # exe app        
        self.main.actions.exe_app_in_client_display(text)
        return
    



    
    def initpref(self):
        # init pref window and buttons
        self.main.pref = self.main.ui.get_widget('prefwindow')            
        self.main.pref.hide()
        self.main.pref.set_icon_from_file(shared.IMG_DIR +\
                                 'tcos-icon-32x32.png')
        # dont destroy window
        # http://www.async.com.br/faq/pygtk/index.py?req=show&file=faq10.006.htp
        self.main.pref.connect('delete-event', self.main.prefwindow_close )
        
        # buttons
        self.main.pref_ok = self.ui.get_widget('pref_ok_button')
        self.main.pref_ok.connect('clicked', self.main.actions.on_pref_ok_button_click)
        self.main.pref_cancel = self.ui.get_widget('pref_cancel_button')
        self.main.pref_cancel.connect('clicked', self.main.actions.on_pref_cancel_button_click)
        
        # make pref widgets
        self.main.pref_spin_update = self.main.ui.get_widget('spin_update')
        self.main.pref_cache_timeout = self.main.ui.get_widget('spin_cache_timeout')
        self.main.pref_scrotsize = self.main.ui.get_widget('spin_scrotsize')
        self.main.pref_miniscrotsize = self.main.ui.get_widget('spin_miniscrotsize')
        self.main.pref_xmlrpc_username = self.main.ui.get_widget('xmlrpc_username')
        self.main.pref_xmlrpc_password = self.main.ui.get_widget('xmlrpc_password')
        
        # populate selects (only on startup)
        self.main.combo_network_interfaces = self.main.ui.get_widget('combo_networkinterface') 
        self.populate_select(self.main.combo_network_interfaces, self.main.config.GetAllNetworkInterfaces() )
        
        # scan method
        self.main.pref_combo_scan_method = self.main.ui.get_widget('combo_scanmethod')
        self.populate_select(self.main.pref_combo_scan_method, shared.scan_methods )
        
        # static host list button
        self.main.pref_open_static = self.main.ui.get_widget('button_open_static')
        self.main.pref_open_static.connect('clicked', self.main.actions.on_button_open_static)
        
        # add signal changed to scan_method to enable/disable button on the fly
        self.main.pref_combo_scan_method.connect('changed', self.main.actions.on_scan_method_change)
        
        
        # checkboxes
        self.main.pref_populatelistatstartup = self.main.ui.get_widget('ck_showliststartup')
        self.main.pref_cybermode = self.main.ui.get_widget('ck_cybermode')
        self.main.pref_systemprocess = self.main.ui.get_widget('ck_systemprocess')
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
        
    def populate_pref(self):
        # set default for combos
        self.set_active_in_select(self.main.pref_combo_scan_method,\
                         self.main.config.GetVar("scan_network_method"))
        self.set_active_in_select(self.main.combo_network_interfaces,\
                         self.main.config.GetVar("network_interface"))
                         
        if self.main.config.GetVar("scan_network_method") != "static":
            self.main.pref_open_static.set_sensitive(False)
        else:
            self.main.pref_open_static.set_sensitive(True)
        
        # set value of spin
        self.main.pref_spin_update.set_value( float(self.main.config.GetVar("refresh_interval")) )
        self.main.pref_cache_timeout.set_value( float(self.main.config.GetVar("cache_timeout")) )
        self.main.pref_scrotsize.set_value( float(self.main.config.GetVar("scrot_size")) )
        self.main.pref_miniscrotsize.set_value( float(self.main.config.GetVar("miniscrot_size")) )
        
        # set value of text widgets
        self.main.pref_xmlrpc_username.set_text(\
                     self.main.config.GetVar("xmlrpc_username").replace('"', '') )
                     
        self.main.pref_xmlrpc_password.set_text(\
                     self.main.config.GetVar("xmlrpc_password").replace('"', '') )
        
        
        # populate checkboxes
        self.populate_checkboxes(self.main.pref_populatelistatstartup, "populate_list_at_startup")
        self.populate_checkboxes(self.main.pref_cybermode, "work_as_cyber_mode")
        self.populate_checkboxes(self.main.pref_systemprocess, "systemprocess")
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
    
    def init_hostlist(self):
        print_debug ( "init_hostlist()" )
        
        self.main.tabla = self.ui.get_widget('hostlist')
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
        self.main.tabla_file.connect("changed", self.main.actions.on_hostlist_click)
        # allow to work right click
        self.main.tabla.connect_object("button_press_event", self.main.actions.on_hostlist_event, self.main.menu)
        return


    def on_sel_click(self, cell, path, model, col=0):
        # reverse status of sel row (saved in COL_SEL_ST)
        iter = model.get_iter(path)
        self.model.set_value(iter, col, not model[path][col])
        print_debug("on_sel_click() ip=%s status=%s" %(model[path][COL_IP], model[path][col]))
        return True

if __name__ == '__main__':
    init=Initialize (None)
    
