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
        self.model=gtk.ListStore(str, str, str, 
                                 gtk.gdk.Pixbuf, gtk.gdk.Pixbuf, gtk.gdk.Pixbuf, 
                                 str, str, bool,bool)
        
        self.main.updating=True
        
        self.searching=False  # boolean True thread running False not running

        self.main.statusbar=self.ui.get_object('statusbar')
        
        self.main.viewtabs=self.ui.get_object('viewtabs')
        self.main.viewtabs.set_property('show-tabs', False)
        self.main.viewtabs.connect("switch_page", self.on_viewtabs_change)
        
        self.ask_mode=None
        
    def on_viewtabs_change(self, widget, pointer, tabnum):
        if tabnum != 0:
            self.main.searchbutton.set_sensitive(False)
            self.main.searchtxt.set_sensitive(False)
        else:
            self.main.searchbutton.set_sensitive(True)
            self.main.searchtxt.set_sensitive(True)
    
    def init_progressbar(self):
        self.main.progressbar=self.ui.get_object('progressbar')
        self.main.progressbutton=self.ui.get_object('progressbutton')
        self.main.progressbutton.connect('clicked', 
                                    self.main.actions.on_progressbutton_click )
        self.main.progressbar.hide()
        self.main.progressbox=self.ui.get_object('progressbox')
        

        
    def initbuttons(self):
        print_debug ( "initbuttons()" )
        self.main.quitbutton = self.ui.get_object('quitbutton')
        self.main.quitbutton.connect('clicked', self.main.quitapp)
        
        self.main.preferencesbutton = self.ui.get_object('preferencesbutton')
        self.main.preferencesbutton.connect('clicked', 
                                self.main.actions.on_preferencesbutton_click)
        
        self.main.refreshbutton = self.ui.get_object('refreshbutton')
        self.main.refreshbutton.connect('clicked', 
                                self.main.actions.on_refreshbutton_click)
        
        self.main.fullscreenbutton = self.ui.get_object('fullscreenbutton')
        self.main.fullscreenbutton.connect('clicked', 
                                self.main.actions.on_fullscreenbutton_click)
        
        self.main.allhostbutton = self.ui.get_object('allhostbutton')
        self.main.allhostbutton.connect('clicked', 
                                self.main.actions.on_allhostbutton_click)
        
        self.main.aboutbutton = self.ui.get_object('aboutbutton')
        self.main.aboutbutton.connect('clicked', 
                                self.main.actions.on_aboutbutton_click)
        
        
        self.main.searchbutton = self.ui.get_object('searchbutton')
        self.main.searchbutton.connect('clicked', 
                                self.main.actions.on_searchbutton_click)
        
        self.main.searchtxt = self.ui.get_object('searchtxt')
        self.main.searchtxt.connect('activate', self.main.search_host)

        self.main.toolbar2 = self.ui.get_object('toolbar2')

        self.main.button_audio = self.ui.get_object('button_audio')
        self.main.handlebox_audio = self.ui.get_object('handlebox_audio')
        self.main.button_audio.connect('clicked', 
                                        self.main.button_actions, "audio")

        self.main.button_chat = self.ui.get_object('button_chat')
        self.main.handlebox_chat = self.ui.get_object('handlebox_chat')
        self.main.button_chat.connect('clicked', 
                                       self.main.button_actions, "chat")

        self.main.button_list = self.ui.get_object('button_list')
        self.main.handlebox_list = self.ui.get_object('handlebox_list')
        self.main.button_list.connect('clicked', 
                                       self.main.button_actions, "list")

        self.main.button_video = self.ui.get_object('button_video')
        self.main.handlebox_video = self.ui.get_object('handlebox_video')
        self.main.button_video.connect('clicked', 
                                        self.main.button_actions, "video")

        self.main.button_send = self.ui.get_object('button_send')
        self.main.handlebox_send = self.ui.get_object('handlebox_send')
        self.main.button_send.connect('clicked', 
                                       self.main.button_actions, "send")

        self.main.button_exe = self.ui.get_object('button_exe')
        self.main.handlebox_exe = self.ui.get_object('handlebox_exe')
        self.main.button_exe.connect('clicked', self.main.button_actions, "exe")

        self.main.button_text = self.ui.get_object('button_text')
        self.main.handlebox_text = self.ui.get_object('handlebox_text')
        self.main.button_text.connect('clicked', self.main.button_actions, "text")

        for button in ['button_audio', 'button_chat', 
                       'button_list', 'button_video', 
                       'button_send', 'button_exe', 'button_text']:
            
            if os.path.isfile(shared.IMG_DIR + "/%s.png" %(button)):
                img=self.ui.get_object( button.replace("button", "image") )
                if img:
                    img.set_from_file(shared.IMG_DIR + "/%s.png" %(button) )
                else:
                    print_debug("WARNING: Error loading button image %s"%button)
            else:
                print_debug("WARNING: Image file '%s' don't exists" 
                            %(shared.IMG_DIR + "/%s.png" %(button)) )


    def initabouttcos(self):
        self.aboutui = gtk.Builder()
        
        self.aboutui.set_translation_domain(shared.PACKAGE)
        self.aboutui.add_from_file(shared.GLADE_DIR + 'tcosmonitor-abouttcos.ui')
        
        self.main.abouttcos = self.aboutui.get_object('abouttcos')
        self.main.abouttcos.hide()
        self.main.abouttcos.set_icon_from_file(shared.IMG_DIR +'tcos-icon-32x32.png')
        
        self.main.abouttabs = self.aboutui.get_object('abouttabs')
        
        #self.main.abouttcos.connect("close", self.on_about_close)
        self.main.abouttcos.connect("delete_event", self.main.actions.on_abouttcos_close)
        
        self.main.abouttcos_version=self.aboutui.get_object('abouttcos_version')
        self.main.abouttcos_version.set_text(shared.version)
        
        self.main.donateurllabel = self.aboutui.get_object('donateurllabel')
        
        self.main.abouttcos_donatebutton = self.aboutui.get_object('abouttcos_donatebutton')
        self.main.abouttcos_donatebutton.connect('clicked', self.main.actions.on_donateurl_click)
        
        # LOAD LICENSE_FILE in TextView
        self.main.abouttcos_license = self.aboutui.get_object('abouttcos_license')
        textbuffer = self.main.abouttcos_license.get_buffer()
        if os.path.isfile(shared.LICENSE_FILE):
            fd1=open(shared.LICENSE_FILE, "r")
            data=fd1.read()
            fd1.close()
            textbuffer.set_text(data)
        else:
            textbuffer.set_text( _("GPL-2 license file not found") )
        
        self.main.abouttcos_logo = self.aboutui.get_object('abouttcos_logo')
        self.main.abouttcos_logo.set_from_file(shared.IMG_DIR +'tcos-logo.png')
        
        self.main.abouttcos_webbutton = self.aboutui.get_object('abouttcos_webbutton')
        self.main.abouttcos_webbutton.connect('clicked', self.main.actions.on_weburl_click)
        
        self.main.abouttcos_donatecheck = self.aboutui.get_object('abouttcos_donatecheck')
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


if __name__ == '__main__':
    init=Initialize (None)
    
