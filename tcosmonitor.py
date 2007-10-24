#!/usr/bin/env python
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
import os

if not os.path.isfile("Initialize.py"):
	#print "DEBUG: append tcosmonitor dir"
	sys.path.append("/usr/share/tcosmonitor")

import pygtk
pygtk.require('2.0')
from gtk import *
import gtk.glade

from time import time, sleep
import getopt
from gettext import gettext as _
from subprocess import Popen, PIPE, STDOUT
import popen2
from threading import Thread
#import threading

# deprecated
#gtk.threads_init()
gtk.gdk.threads_init()

import gobject

import shared




def print_debug(txt):
    if shared.debug:
        print "%s::%s" %("tcosmonitor", txt)
    return

def crono(start, txt):
    print_debug ("crono(), %s get %f seconds" %(txt, (time() - float(start))) )
    return

def usage():
    print "TcosMonitor help:"
    print ""
    print "   tcosmonitor -d [--debug]  (write debug data to stdout)"
    print "   tcosmonitor -h [--help]   (this help)"


try:
    opts, args = getopt.getopt(sys.argv[1:], ":hd", ["help", "debug"])
except getopt.error, msg:
    print msg
    print "for command line options use tcosconfig --help"
    sys.exit(2)

# process options
for o, a in opts:
    if o in ("-d", "--debug"):
        print "DEBUG ACTIVE"
        shared.debug = True
    if o in ("-h", "--help"):
        usage()
        sys.exit()



import Initialize
import TcosXmlRpc
import LocalData
import TcosConf
import TcosActions
import TcosXauth

class TcosMonitor:
    def __init__(self):
        # if true auto-update is active, false only one update        
        self.updating=False
        self.name="TcosMonitor"
        
        self.worker_running=False
        
        #import shared
        gtk.glade.bindtextdomain(shared.PACKAGE, shared.LOCALE_DIR)
        gtk.glade.textdomain(shared.PACKAGE)
        
        # Widgets
        self.ui = gtk.glade.XML(shared.GLADE_DIR + 'tcosmonitor.glade')
        self.mainwindow = self.ui.get_widget('mainwindow')
        self.mainwindow.set_icon_from_file(shared.IMG_DIR +\
                                     'tcos-icon-32x32.png')
        #self.pref = self.ui.get_widget('prefwindow')
        #self.main.fullscreen()
        self.is_fullscreen=False
        
        # close windows signals
        self.mainwindow.connect('destroy', self.quitapp )
        self.mainwindow.connect("delete_event", self.quitapp)
        #self.pref.connect('destroy', self.prefwindow_close )
        #self.pref.hide()
        
        
        # FIXME
        self.scrolledtextview = self.ui.get_widget('scrolledtextview')
        import htmltextview
        #htmltextview.HtmlHandler().set_main(self)
        
        self.datatxt = htmltextview.HtmlTextView(self)
        self.datatxt.show()
        self.scrolledtextview.add(self.datatxt)
        self.datatxt.clean()
        
        
        
        # init classes
        self.config=TcosConf.TcosConf(self)
        self.localdata=LocalData.LocalData(self)
        self.xmlrpc=TcosXmlRpc.TcosXmlRpc(self)
        self.xauth=TcosXauth.TcosXauth(self)
        
        
        self.init=Initialize.Initialize(self)
        self.actions=TcosActions.TcosActions(self)
        
        
        
        #########  init some elements ###########
        self.init.init_progressbar()
        self.init.initabout()
        self.init.initask()
        self.init.initpref()
        self.init.populate_pref()
        #########################################
        
        self.actions.update_hostlist()
        self.init.initbuttons()
        
        # make menus
        self.actions.RightClickMenuOne(None)
        self.actions.RightClickMenuAll()
        
        # init hostlist
        self.init.init_hostlist()
        
        if not shared.dbus_disabled:
            from TcosDBus import TcosDBusAction
            self.dbus_action=TcosDBusAction(self, admin=self.config.GetVar("xmlrpc_username"),
                                  passwd=self.config.GetVar("xmlrpc_password")  )
        
        
        # generate host list if checked
        if self.config.GetVar("populate_list_at_startup") == "1":
            self.populate_host_list()
        
        # create tmp dir
        p = popen2.Popen3("mkdir /tmp/tcos_share/")
        p.wait()
        
    def prefwindow_close(self, widget, event):
        print_debug ( "prefwindow_close() closing preferences window" )
        self.pref.hide()
        return True
    


    

    def search_host(self, widget):
        print_debug ( "search_host()" )
        txt=self.searchtxt.get_text()
        if txt == "":
            allclients=self.localdata.GetAllClients( self.config.GetVar("scan_network_method") )
            Thread( target=self.actions.populate_hostlist, args=([allclients]) ).start()
        #print txt
        model=self.tabla.get_model()
        notvalid=[]
        model.foreach(self.delete_not_searched, (notvalid))
        notvalid.reverse()
        for host in notvalid:
            model.remove( model.get_iter(host) )
        
    def delete_not_searched(self, model, path, iter, data):
        txt=self.searchtxt.get_text()
        hostname=model.get_value(iter, 0)
        ip=model.get_value(iter, 1)
        username=model.get_value(iter, 2)
        if txt != hostname and txt != ip and txt != username:
            data.append(path)
  

    

    def exe_cmd(self, cmd):
        print_debug ( "exe_cmd() cmd=%s" %(cmd) )
        self.p = Popen(cmd, shell=True, bufsize=0, stdout=PIPE, stderr=STDOUT)
    
    def write_into_statusbar(self, msg, *args):
        #print_debug("STATUSBAR: Writing \"%s\" into statusbar" % msg)
        context_id=self.statusbar.get_context_id("status")
        self.statusbar.pop(context_id)
        self.statusbar.push(context_id, msg)
        return    

    def quitapp(self,*args):
        print_debug ( _("Exiting") )
        #gtk.main_quit()
        p = popen2.Popen3("rm -rf /tmp/tcos_share/")
        p.wait()
        self.mainloop.quit()


    def run (self):
        self.mainloop = gobject.MainLoop()
        try:
            self.mainloop.run()
        except KeyboardInterrupt: # Press Ctrl+C
            self.quitapp()
        
        
    
if __name__ == '__main__':
    app = TcosMonitor ()
    # Run app
    app.run ()
