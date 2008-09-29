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
""" template extension """

from gettext import gettext as _


from tcosmonitor import shared
from tcosmonitor.TcosExtensions import TcosExtension

from shutil import copy
import os
import gtk
#import subprocess
#import signal

def print_debug(txt):
    if shared.debug:
        print "%s::%s" % ("extensions::sendfiles", txt)
    return


class SendFiles(TcosExtension):
    def register(self):
        self.main.menus.register_simple( _("Send files") , "menu_send.png", 2, self.send_one, "send")
        self.main.menus.register_all( _("Send files") , "menu_send.png", 2, self.send_all, "send")
        

    def send_one(self, widget, ip):
        if not self.get_client():
            return
        # action sent by vidal_joshur at gva dot es
        # send files
        # search for connected users
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg ( _("Can't send files, user is not logged") )
            return
        
        str_scapes=[" ", "(", ")", "*", "!", "?", "\"", "`", "[", "]", "{", "}", ";", ":", ",", "=", "$"]

        dialog = gtk.FileChooserDialog( _("Select file or files..."),
                           None,
                           gtk.FILE_CHOOSER_ACTION_OPEN,
                           (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        #dialog.set_select_multiple(select_multiple)
        dialog.set_select_multiple(True)
        self.folder = self._folder = os.environ['HOME']
        dialog.set_current_folder(self.folder)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        
        
        if not os.path.isdir("/tmp/tcos_share"):
            shared.info_msg( _("TcosMonitor need special configuration for rsync daemon to send files.\n\nPlease read configuration requeriments in:\n/usr/share/doc/tcosmonitor/README.rsync") )
            return
        
        for filename in os.listdir("/tmp/tcos_share/"):
            if os.path.isfile("/tmp/tcos_share/%s" %filename):
                os.remove("/tmp/tcos_share/%s" %filename)
                    
        response = dialog.run()
        
        if response == gtk.RESPONSE_OK:
                            
            filenames = dialog.get_filenames()
            
            rsync_filenames_client = ""
            rsync_filenames_server = ""
            basenames = ""
            for filename in filenames:
                if filename.find("\\") != -1 or filename.find("'") != -1 or filename.find("&") != -1:
                    dialog.destroy()
                    msg=_("Special characters used in \"%s\".\nPlease rename it." %os.path.basename(filename) )
                    shared.info_msg( msg )
                    return
                basename_scape=os.path.basename(filename)
                abspath_scape=filename
                for scape in str_scapes:
                    basename_scape=basename_scape.replace("%s" %scape, "\%s" %scape)
                    abspath_scape=abspath_scape.replace("%s" %scape, "\%s" %scape)
                rsync_filenames_client += "\"tcos_share/%s\" " % ( basename_scape )
                rsync_filenames_server += "%s " % ( abspath_scape )
                basenames += "%s\n" % ( os.path.basename(filename) )
                copy(filename, "/tmp/tcos_share/")
                os.chmod("/tmp/tcos_share/%s" %os.path.basename(filename), 0644)
                
            self.main.write_into_statusbar( _("Waiting for send files...") )
            
            newusernames=[]
            
            for user in self.connected_users:
                if user.find(":") != -1:
                    #usern, ip=user.split(":")
                    #self.main.xmlrpc.newhost(ip)
                    server=self.main.xmlrpc.GetStandalone("get_server")
                    standalone_cmd = "/usr/lib/tcos/rsync-controller %s %s %s" % ( _("Teacher"), server, rsync_filenames_client.strip() )
                    self.main.xmlrpc.DBus("exec", standalone_cmd )
                    self.main.xmlrpc.DBus("mess", _("Teacher has sent some files to %(teacher)s folder:\n\n%(basenames)s")  %{"teacher":_("Teacher"), "basenames":basenames} )
                else:
                    newusernames.append(user)
            
            thin_cmd = "/usr/lib/tcos/rsync-controller %s %s %s" % ( _("Teacher"), "localhost", rsync_filenames_client.strip() )
            
            result = self.main.dbus_action.do_exec( newusernames , thin_cmd )
            
            if not result:
                shared.error_msg ( _("Error while exec remote app:\nReason:%s") %( self.main.dbus_action.get_error_msg() ) )
                self.main.write_into_statusbar( _("Error creating destination folder.") )
            else:
                result = self.main.dbus_action.do_message(newusernames ,
                            _("Teacher has sent some files to %(teacher)s folder:\n\n%(basenames)s") %{"teacher":_("Teacher"), "basenames":basenames} )
            self.main.write_into_statusbar( _("Files sent.") )
        dialog.destroy()

    def send_all(self, *args):
        if not self.get_all_clients():
            return
        # action sent by vidal_joshur at gva dot es
        # send files
        # search for connected users
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg( _("No users logged.") )
            return
        
        str_scapes=[" ", "(", ")", "*", "!", "?", "\"", "`", "[", "]", "{", "}", ";", ":", ",", "=", "$"]
        
        dialog = gtk.FileChooserDialog( _("Select file or files..."),
                           None,
                           gtk.FILE_CHOOSER_ACTION_OPEN,
                           (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        #dialog.set_select_multiple(select_multiple)
        dialog.set_select_multiple(True)
        self.folder = self._folder = os.environ['HOME']
        dialog.set_current_folder(self.folder)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        
        
        if not os.path.isdir("/tmp/tcos_share"):
            shared.info_msg( _("TcosMonitor need special configuration for rsync daemon to send files.\n\nPlease read configuration requeriments in:\n/usr/share/doc/tcosmonitor/README.rsync") )
            return
        
        for filename in os.listdir("/tmp/tcos_share/"):
            if os.path.isfile("/tmp/tcos_share/%s" %filename):
                os.remove("/tmp/tcos_share/%s" %filename)
                    
        response = dialog.run()
        
        if response == gtk.RESPONSE_OK:
            
            filenames = dialog.get_filenames()
            
            rsync_filenames_client = ""
            rsync_filenames_server = ""
            basenames = ""
            for filename in filenames:
                if filename.find("\\") != -1 or filename.find("'") != -1 or filename.find("&") != -1:
                    dialog.destroy()
                    msg=_("Special characters used in \"%s\".\nPlease rename it." %os.path.basename(filename) )
                    shared.info_msg( msg )
                    return
                basename_scape=os.path.basename(filename)
                abspath_scape=filename
                for scape in str_scapes:
                    basename_scape=basename_scape.replace("%s" %scape, "\%s" %scape)
                    abspath_scape=abspath_scape.replace("%s" %scape, "\%s" %scape)
                rsync_filenames_client += "\"tcos_share/%s\" " % ( basename_scape )
                rsync_filenames_server += "%s " % ( abspath_scape )
                basenames += "%s\n" % ( os.path.basename(filename) )
                copy(filename, "/tmp/tcos_share/")
                os.chmod("/tmp/tcos_share/%s" %os.path.basename(filename), 0644)
            
            self.main.write_into_statusbar( _("Waiting for send files...") )
            
            newusernames=[]
            
            for user in self.connected_users:
                if user.find(":") != -1:
                    usern, ip=user.split(":")
                    self.main.xmlrpc.newhost(ip)
                    server=self.main.xmlrpc.GetStandalone("get_server")
                    standalone_cmd = "/usr/lib/tcos/rsync-controller %s %s %s" % ( _("Teacher"), server, rsync_filenames_client.strip() )
                    self.main.xmlrpc.DBus("exec", standalone_cmd )
                    self.main.xmlrpc.DBus("mess", _("Teacher has sent some files to %(teacher)s folder:\n\n%(basenames)s")  %{"teacher":_("Teacher"), "basenames":basenames} )
                else:
                    newusernames.append(user)
            
            thin_cmd = "/usr/lib/tcos/rsync-controller %s %s %s" % ( _("Teacher"), "localhost", rsync_filenames_client.strip() )
            
            result = self.main.dbus_action.do_exec( newusernames , thin_cmd )
            
            if not result:
                shared.error_msg ( _("Error while exec remote app:\nReason:%s") %( self.main.dbus_action.get_error_msg() ) )
                self.main.write_into_statusbar( _("Error creating destination folder.") )
            else:
                result = self.main.dbus_action.do_message(newusernames ,
                            _("Teacher has sent some files to %(teacher)s folder:\n\n%(basenames)s") %{"teacher":_("Teacher"), "basenames":basenames} )
            
            self.main.write_into_statusbar( _("Files sent.") )
        dialog.destroy()


__extclass__=SendFiles
