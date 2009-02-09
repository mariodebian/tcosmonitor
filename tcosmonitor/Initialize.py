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
import os
#import urllib2
#from os import remove, path
#from threading import Thread
#from subprocess import Popen, PIPE, STDOUT

#from time import sleep, localtime
#import gobject
#import string

#COL_HOST, COL_IP, COL_USERNAME, COL_ACTIVE, COL_LOGGED,\
# COL_BLOCKED, COL_PROCESS, COL_TIME, COL_SEL, COL_SEL_ST = range(10)


# constant to font sizes
PANGO_SCALE=1024



def print_debug(txt):
    if shared.debug:
        print "%s::%s" % (__name__, txt)

def crono(start, txt):
    print_debug ("crono(), %s get %f seconds" %(txt, (time() - start)) )
    return



class Initialize(object):

    def __init__(self, main):
        print_debug ( "__init__() starting" )
        self.main=main
        self.ui=self.main.ui
        self.model=gtk.ListStore\
        (str, str, str, gtk.gdk.Pixbuf, gtk.gdk.Pixbuf, gtk.gdk.Pixbuf, str, str, bool,bool)
        
        self.main.updating=True
        
        self.searching=False  # boolean True thread running False not running

        self.main.statusbar=self.ui.get_widget('statusbar')
        
        self.main.viewtabs=self.ui.get_widget('viewtabs')
        self.main.viewtabs.set_property('show-tabs', False)
        self.main.viewtabs.connect("switch_page", self.on_viewtabs_change)
        
        self.ask_mode=None
        
    def on_viewtabs_change(self, widget, pointer, tabnum):
        if tabnum != 0:
            if shared.lab:
                self.main.searchbutton.set_sensitive(True)
                self.main.searchtxt.set_sensitive(True)
            else:
                self.main.searchbutton.set_sensitive(False)
                self.main.searchtxt.set_sensitive(False)
        else:
            self.main.searchbutton.set_sensitive(True)
            self.main.searchtxt.set_sensitive(True)
    """
    def get_widget(self, wname):
        widgets = gtk.glade.XML( shared.GLADE_DIR + 'tcosmonitor.glade', wname )
        return widgets.get_widget( wname )
    """
    
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
        #if shared.lab:
        tooltip=gtk.Tooltips()
        self.main.quitbutton.set_tooltip(tooltip,_("Quit from TcosMonitor"))
        
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

        self.main.toolbar2 = self.ui.get_widget('toolbar2')

        self.main.button_audio = self.ui.get_widget('button_audio')
        self.main.handlebox_audio = self.ui.get_widget('handlebox_audio')
        self.main.button_audio.connect('clicked', self.main.button_actions, "audio")

        self.main.button_chat = self.ui.get_widget('button_chat')
        self.main.handlebox_chat = self.ui.get_widget('handlebox_chat')
        self.main.button_chat.connect('clicked', self.main.button_actions, "chat")

        self.main.button_list = self.ui.get_widget('button_list')
        self.main.handlebox_list = self.ui.get_widget('handlebox_list')
        self.main.button_list.connect('clicked', self.main.button_actions, "list")

        self.main.button_video = self.ui.get_widget('button_video')
        self.main.handlebox_video = self.ui.get_widget('handlebox_video')
        self.main.button_video.connect('clicked', self.main.button_actions, "video")

        self.main.button_send = self.ui.get_widget('button_send')
        self.main.handlebox_send = self.ui.get_widget('handlebox_send')
        self.main.button_send.connect('clicked', self.main.button_actions, "send")

        self.main.button_exe = self.ui.get_widget('button_exe')
        self.main.handlebox_exe = self.ui.get_widget('handlebox_exe')
        self.main.button_exe.connect('clicked', self.main.button_actions, "exe")

        self.main.button_text = self.ui.get_widget('button_text')
        self.main.handlebox_text = self.ui.get_widget('handlebox_text')
        self.main.button_text.connect('clicked', self.main.button_actions, "text")

        self.main.button_share = self.ui.get_widget('button_share')
        self.main.handlebox_share = self.ui.get_widget('handlebox_share')
        self.main.button_share.connect('clicked', self.main.button_actions, "share")
        self.main.handlebox_share.hide()

        for button in ['button_audio', 'button_chat', 'button_list', 'button_video', 'button_send', 'button_exe', 'button_text']:
            
            if os.path.isfile(shared.IMG_DIR + "/%s.png" %(button)):
                img=self.ui.get_widget( button.replace("button", "image") )
                if img:
                    img.set_from_file(shared.IMG_DIR + "/%s.png" %(button) )
                else:
                    print_debug("WARNING: Error loading button image %s"%button)
            else:
                print_debug("WARNING: Image file '%s' don't exists" %(shared.IMG_DIR + "/%s.png" %(button)) )

        """
        <property name="pixbuf">/usr/share/tcosmonitor/images/button_rtp.png</property>
        <property name="pixbuf">/usr/share/tcosmonitor/images/button_chat.png</property>
        <property name="pixbuf">/usr/share/tcosmonitor/images/button_list.png</property>
        <property name="pixbuf">/usr/share/tcosmonitor/images/button_broadcast.png</property>
        <property name="pixbuf">/usr/share/tcosmonitor/images/button_send.png</property>
        <property name="pixbuf">/usr/share/tcosmonitor/images/button_exec.png</property>
        <property name="pixbuf">/usr/share/tcosmonitor/images/button_msg.png</property>
        """
        if shared.lab:
            self.main.quitbutton.set_tooltip(tooltip,_("Salir de Lliurex Lab"))
            self.lab_change_buttons()

    def __change_toolbutton_icon(self, widget, imgfile):
        img=gtk.Image()
        img.set_from_file(imgfile)
        img.show()
        widget.set_icon_widget(img)

    def lab_change_buttons(self):
        self.__change_toolbutton_icon( self.main.quitbutton, shared.IMG_DIR +'button_exit.png')
        self.__change_toolbutton_icon( self.main.preferencesbutton, shared.IMG_DIR +'button_pref.png')
        self.__change_toolbutton_icon( self.main.refreshbutton, shared.IMG_DIR + 'button_refresh.png')
        self.__change_toolbutton_icon( self.main.allhostbutton, shared.IMG_DIR + 'button_all.png')
        self.__change_toolbutton_icon( self.main.searchbutton, shared.IMG_DIR + 'button_search.png')
        

    def initabouttcos(self):
        self.main.abouttcos = self.main.ui.get_widget('abouttcos')
        self.main.abouttcos.hide()
        self.main.abouttcos.set_icon_from_file(shared.IMG_DIR +'tcos-icon-32x32.png')
        if shared.lab:
            self.main.abouttcos.set_icon_from_file(shared.IMG_DIR +'lliurex-lab.png')
        
        self.main.abouttabs = self.main.ui.get_widget('abouttabs')
        
        #self.main.abouttcos.connect("close", self.on_about_close)
        self.main.abouttcos.connect("delete_event", self.main.actions.on_abouttcos_close)
        
        self.main.abouttcos_version=self.main.ui.get_widget('abouttcos_version')
        self.main.abouttcos_version.set_text(shared.version)
        
        self.main.donateurllabel = self.ui.get_widget('donateurllabel')
        
        self.main.abouttcos_donatebutton = self.ui.get_widget('abouttcos_donatebutton')
        self.main.abouttcos_donatebutton.connect('clicked', self.main.actions.on_donateurl_click)
        
        # LOAD LICENSE_FILE in TextView
        self.main.abouttcos_license = self.ui.get_widget('abouttcos_license')
        textbuffer = self.main.abouttcos_license.get_buffer()
        if os.path.isfile(shared.LICENSE_FILE):
            fd1=open(shared.LICENSE_FILE, "r")
            data=fd1.read()
            fd1.close()
            textbuffer.set_text(data)
        else:
            textbuffer.set_text( _("GPL-2 license file not found") )
        
        self.main.abouttcos_logo = self.ui.get_widget('abouttcos_logo')
        self.main.abouttcos_logo.set_from_file(shared.IMG_DIR +'tcos-logo.png')
        if shared.lab:
            self.main.abouttcos_logo.set_from_file(shared.IMG_DIR +'tcos-lliurex-logo.png')
        
        self.main.abouttcos_webbutton = self.ui.get_widget('abouttcos_webbutton')
        self.main.abouttcos_webbutton.connect('clicked', self.main.actions.on_weburl_click)
        
        self.main.abouttcos_donatecheck = self.ui.get_widget('abouttcos_donatecheck')
        self.main.abouttcos_donatecheck.connect('toggled', self.main.actions.on_abouttcos_donatecheck_change)
        
        if self.main.config.GetVar("show_about") == 1:
            self.main.abouttcos.show()
            self.main.abouttabs.set_current_page(0)
            self.main.config.SetVar("show_about", "0")
            self.main.config.SaveToFile()

        if self.main.config.GetVar("show_donate") == 1:
            self.main.abouttcos.show()
            self.main.abouttabs.set_current_page(self.main.abouttabs.get_n_pages()-1)
            self.main.abouttcos_donatecheck.set_active(False)
        else:
            self.main.abouttcos_donatecheck.set_active(True)
            
        if shared.lab:
            self.main.about_title = self.ui.get_widget('label149')
            self.main.about_title.set_markup( _("<span size=\"xx-large\">Lliurex Lab</span>")  )
            self.main.abouttcos.set_title( _("About Lliurex Lab")  )
            #self.main.abouttabs.remove_page(4)
        
        
    
#    def initask(self):
#        self.main.ask_ip=None
#        
#        self.main.ask = self.main.ui.get_widget('askwindow')
#        self.main.ask.connect('delete-event', self.main.actions.askwindow_close )
#        self.main.ask.set_icon_from_file(shared.IMG_DIR +'tcos-icon-32x32.png')
#        
#        
#        self.main.ask_label = self.main.ui.get_widget('txt_asklabel')
#        ## arrastrar y soltar
#        self.main.ask_fixed = self.main.ui.get_widget('ask_fixed')
#        self.main.ask_dragdrop = self.main.ui.get_widget('label99')
#        self.main.image_entry = self.main.ui.get_widget('image_askentry')
#        self.main.image_entry.drag_dest_set( gtk.DEST_DEFAULT_ALL, \
#                                  [( 'text/uri-list', 0, 2 ),], gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_COPY)
#        self.main.image_entry.connect( 'drag_data_received', self.main.actions.on_drag_data_received)
#        self.main.ask_fixed.hide()
#        self.main.image_entry.hide()
#        self.main.ask_dragdrop.hide()
#        ## fin arrastrar y soltar
#        self.liststore = gtk.ListStore(str)
#        for s in shared.appslist:
#            self.liststore.append([s])
#            
#        self.main.ask_entry = self.main.ui.get_widget('txt_askentry')
#        self.main.ask_completion = gtk.EntryCompletion()
#        self.main.ask_completion.set_model(self.liststore)
#        self.main.ask_entry.set_completion(self.main.ask_completion)
#        self.main.ask_completion.set_text_column(0)
#        
#        self.main.ask_completion.connect('match-selected', self.match_cb)
#        self.main.ask_entry.connect('activate', self.activate_cb)
#        
#        self.main.ask_cancel = self.main.ui.get_widget('ask_cancelbutton')
#        self.main.ask_exec = self.main.ui.get_widget('ask_exebutton')
#        
#        # buttons signals
#        self.main.ask_exec.connect('clicked', self.main.actions.on_ask_exec_click)
#        self.main.ask_cancel.connect('clicked', self.main.actions.on_ask_cancel_click)
        
    
#    def match_cb(self, completion, model, iter):
#        print_debug ( "match_cb() " )
#        print_debug( "%s was selected" %(model[iter][0]) )
#        self.main.actions.exe_app_in_client_display(model[iter][0])
#        return
#    
#    def activate_cb(self, entry):
#        text = self.main.ask_entry.get_text()
#        print_debug ( "activate_cb() text=%s" %(text) )
#        
#        # append to liststore
#        if text:
#            if text not in [row[0] for row in self.liststore]:
#                self.liststore.append([text])
#                #self.main.ask_entry.set_text('')
#        
#        # exe app        
#        self.main.actions.exe_app_in_client_display(text)
#        return
    
    """
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
    """

if __name__ == '__main__':
    init=Initialize (None)
    
