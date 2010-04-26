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

#if not os.path.isfile("Initialize.py"):
#    #print "DEBUG: append tcosmonitor dir"
#    sys.path.append("/usr/share/tcosmonitor")

import pygtk
pygtk.require('2.0')
import gtk
#import gtk.glade

from time import time
import getopt
from gettext import gettext as _
from threading import Thread

gtk.gdk.threads_init()

import gobject

from tcosmonitor import shared

import grp, pwd

import gettext

# Medusa 
import asyncore
from medusa import default_handler
from medusa import filesys
from medusa import ftp_server
from medusa import status_handler

# M2Crypto
from tcosmonitor import ftps_server
from threading import Thread
import M2Crypto

class TCOSFTPSERVER (Thread):
    def __init__(self):
         self.FTP_PORT = 8997
         M2Crypto.Rand.load_file('/tmp/randpooltcos.dat', -1) 
         self.ssl_ctx=M2Crypto.SSL.Context('sslv23')
         self.ssl_ctx.load_cert('/etc/tcos/ssl/tcos_server.pem')
         self.ssl_ctx.load_client_CA('/etc/tcos/ssl/tcos_ca.crt')
         self.ssl_ctx.set_verify(M2Crypto.SSL.verify_none, 10)
         self.ssl_ctx.set_session_id_ctx('127.0.0.1:9443')
         self.ssl_ctx.set_tmp_dh('/etc/tcos/ssl/tcos_dh1024.pem')
         self.ssl_ctx.set_info_callback()
         Thread.__init__(self)
    def run(self):
         if not os.path.isdir("/tmp/tcos_share"): os.mkdir("/tmp/tcos_share")
         self.fauthz = ftp_server.anon_authorizer('/tmp/tcos_share')
         self.ftps = ftps_server.ftp_tls_server(self.fauthz, self.ssl_ctx, port=self.FTP_PORT)
         self.ftps.status()
         self.sh=status_handler.status_extension([self.ftps])
         M2Crypto.Rand.save_file('/tmp/randpooltcos.dat')
         asyncore.loop()
         
         
gettext.bindtextdomain(shared.PACKAGE, shared.LOCALE_DIR)
gettext.textdomain(shared.PACKAGE)


def print_debug(txt):
    if shared.debug:
        print >>sys.stderr, "%s::%s" % ("tcosmonitor", txt)
        #print("%s::%s" % ("tcosmonitor", txt), file=sys.stderr)
    return

def crono(start, txt):
    print_debug ("crono(), %s get %f seconds" %(txt, (time() - float(start))) )
    return

def usage():
    print ("TcosMonitor help:")
    print ("")
    print ("   tcosmonitor -d [--debug]  (write debug data to stdout)")
    print ("   tcosmonitor -h [--help]   (this help)")


try:
    OPTS, ARGS = getopt.getopt(sys.argv[1:], ":hd", ["help", "debug"])
except getopt.error, msg:
    print (msg)
    print ("for command line options use tcosconfig --help")
    sys.exit(2)

# process options
for o, a in OPTS:
    if o in ("-d", "--debug"):
        print ("DEBUG ACTIVE")
        shared.debug = True
    if o in ("-h", "--help"):
        usage()
        sys.exit()

import tcosmonitor

class TcosMonitor(object):
    def __init__(self):
        # if true auto-update is active, false only one update        
        self.updating=False
        self.name="TcosMonitor"
        self.force_selected_ip=None
        # register triggers
        self.triggers={}
        self.mainloop = gobject.MainLoop()
        
        self.groupconf=self.loadconf( os.path.abspath(shared.GLOBAL_CONF) )
        
        try:
            if int(self.groupconf['check_tcosmonitor_user_group']) == 1:
                shared.check_tcosmonitor_user_group=True
        except Exception, err:
            print_debug("__init__() Exception getting group, error=%s"%err)
            pass
        
        if self.groupconf['dont_show_users_in_group'] != '':
            shared.dont_show_users_in_group=self.groupconf['dont_show_users_in_group']
        #else:
        #    shared.dont_show_users_in_group=None

        if self.groupconf['tnc_only_ports'] != "no":
            shared.tnc_only_ports="yes"
            
        ##################################################
        
        self.worker_running=False
        self.ingroup_tcos=False
        
        if shared.check_tcosmonitor_user_group:
            for group in os.getgroups():
                if grp.getgrgid(group)[0] == "tcos":
                    self.ingroup_tcos=True
            if os.getuid() == 0:
                self.ingroup_tcos=True
            if self.ingroup_tcos == False and os.getuid() != 0:
                shared.error_msg( _("The user \"%s\" must be member of the group \"tcos\"\
 to exec tcosmonitor.\n\nIf you are system administrator, add your\
 user to tcos group." %pwd.getpwuid(os.getuid())[0]))
                sys.exit(1)

        
        # Widgets
        self.ui = gtk.Builder()
        self.ui.set_translation_domain(shared.PACKAGE)
        print_debug("Loading ui file...")
        self.ui.add_from_file(shared.GLADE_DIR + 'tcosmonitor-mainwindow.ui')
        
        
        self.mainwindow = self.ui.get_object('mainwindow')
        self.mainwindow.set_icon_from_file(shared.IMG_DIR +\
                                     'tcos-icon-32x32.png')
        
        self.is_fullscreen=False
        
        # close windows signals
        self.mainwindow.connect('destroy', self.quitapp )
        self.mainwindow.connect("delete_event", self.quitapp)

        # reduce mainwindow size if running in height < 1024x768
        #>>> gtk.gdk.screen_height()
        #>>> gtk.gdk.screen_width()
        if gtk.gdk.screen_height() < 768:
            print_debug("set lower size of glade mainwindow")
            self.mainwindow.set_size_request(760,520)

        # glade file (mainwindow) visible=False, show now
        self.mainwindow.show()
        
        
        # FIXME
        self.scrolledtextview = self.ui.get_object('scrolledtextview')
        #import htmltextview
        #htmltextview.HtmlHandler().set_main(self)
        
        self.datatxt = tcosmonitor.htmltextview.HtmlTextView(self)
        self.datatxt.show()
        self.scrolledtextview.add(self.datatxt)
        self.datatxt.clean()
        
        
        
        # init classes
        self.common=tcosmonitor.TcosCommon.TcosCommon(self)
        self.config=tcosmonitor.TcosConf.TcosConf(self)
        self.localdata=tcosmonitor.LocalData.LocalData(self)
        self.xmlrpc=tcosmonitor.TcosXmlRpc.TcosXmlRpc(self)
        self.xauth=tcosmonitor.TcosXauth.TcosXauth(self)
        self.preferences=tcosmonitor.TcosPreferences.TcosPreferences(self)
        
        self.menus=tcosmonitor.TcosMenus.TcosMenus(self)
        
        self.actions=tcosmonitor.TcosActions.TcosActions(self)
        
        # views
        self.listview=tcosmonitor.TcosListView.TcosListView(self)
        self.iconview=tcosmonitor.TcosIconView.TcosIconView(self)
        self.classview=tcosmonitor.TcosClassView.TcosClassView(self)
        
        self.init=tcosmonitor.Initialize.Initialize(self)
        
        self.static=tcosmonitor.TcosStaticHosts.TcosStaticHosts(self)
        
        
        #########  init some elements ###########
        self.init.init_progressbar()
        self.init.initabouttcos()
        #########################################
        self.init.initbuttons()
        self.preferences.populate_pref()
        

        
        self.extloader=tcosmonitor.TcosExtensions.TcosExtLoader(self)
        
        
        if not shared.dbus_disabled:
            self.dbus_action=tcosmonitor.TcosDBus.TcosDBusAction(self, 
                                  admin=self.config.GetVar("xmlrpc_username"),
                                  passwd=self.config.GetVar("xmlrpc_password"))
        
        self.stop_running_actions=[]
        # generate host list if checked
        if self.config.GetVar("populate_list_at_startup") == "1":
            self.populate_host_list()
        self.actions.update_hostlist()
            
        try:
            self.ftp_thread = TCOSFTPSERVER() 
            self.ftp_thread.setDaemon(1)
            self.ftp_thread.start()
        except Exception, err:
            pass

    def loadconf(self, conffile):
        conf={}
        print_debug ( "loadconf() conffile=%s" %conffile )
        if os.path.isfile(conffile):
            print_debug ("loadconf() found conf file %s" %conffile)
            f=open(conffile, "r")
            data=f.readlines()
            f.close()
            for line in data:
                if line == '\n':
                    continue
                if line.find('#') == 0:
                    continue
                line=line.replace('\n', '')
                if "=" in line:
                    try:
                        conf["%s"%line.split('=')[0]] = line.split('=')[1].replace('"', '')
                    except Exception, err:
                        print_debug("loadconf() Exception: %s" %err)
                        pass
        print_debug( "loadconf conf=%s" %conf )
        return conf

    def button_actions(self, widget, action):
        print_debug ( "button_actionst() action=%s" %action)

        if action == "audio":
            if self.actions.button_action_audio != None:
                self.actions.button_action_audio()
        elif action == "chat":
            if self.actions.button_action_chat != None:
                self.actions.button_action_chat()
        elif action == "list":
            if self.actions.button_action_list != None:
                self.actions.button_action_list()
        elif action == "video":
            if self.actions.button_action_video != None:
                self.actions.button_action_video()
        elif action == "send":
            if self.actions.button_action_send != None:
                self.actions.button_action_send()
        elif action == "exe":
            if self.actions.button_action_exe != None:
                self.actions.button_action_exe()
        elif action == "text":
            if self.actions.button_action_text != None:
                self.actions.button_action_text()
        return

    def search_host(self, widget):
        print_debug ( "search_host()" )
        txt=self.searchtxt.get_text()
        if txt == "":
            allclients=self.localdata.GetAllClients( self.config.GetVar("scan_network_method") )
            Thread( target=self.actions.populate_hostlist, args=([allclients]) ).start()
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
    
    def write_into_statusbar(self, msg, *args):
        #print_debug("STATUSBAR: Writing \"%s\" into statusbar" % msg)
        context_id=self.statusbar.get_context_id("status")
        self.statusbar.pop(context_id)
        self.statusbar.push(context_id, msg)
        return    

    def quitapp(self, *args):
        print_debug ( _("Exiting") )
        #gtk.main_quit()
        widgets=self.stop_running_actions[:]
        print_debug("Running actions: %s" %len(widgets))
        for widget in widgets:
            print_debug("Stop running action... widget=%s" %(widget))
            try:
                widget.clicked()
            except:
                pass
        if os.path.isdir("/tmp/tcos_share/"):
            for filename in os.listdir("/tmp/tcos_share/"):
                if os.path.isfile("/tmp/tcos_share/%s" %filename):
                    os.remove("/tmp/tcos_share/%s" %filename)
            if os.path.isdir("/tmp/tcos_share"):
                os.rmdir("/tmp/tcos_share")
                
        if os.path.isfile(os.path.expanduser('~/.tcosvnc')):
            os.remove(os.path.expanduser('~/.tcosvnc'))
        
        self.mainloop.quit()


    def run (self):
        try:
            self.mainloop.run()
        except KeyboardInterrupt: # Press Ctrl+C
            self.quitapp()
        
        
    
if __name__ == '__main__':
    app = TcosMonitor ()
    # Run app
    app.run ()
