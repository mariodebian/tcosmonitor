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
""" template extension """

from gettext import gettext as _


from tcosmonitor import shared
from tcosmonitor.TcosExtensions import TcosExtension
import netifaces

from shutil import copy
import os
import gtk
import sys

def print_debug(txt):
    if shared.debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)


class SendFiles(TcosExtension):
    def register(self):
        self.main.actions.button_action_send=self.send_all
        self.main.classview.class_external_send=self.send_external
        
        self.main.menus.register_simple( _("Send files") , "menu_send.png", 2, self.send_one, "send")
        self.main.menus.register_all( _("Send files") , "menu_send.png", 2, self.send_all, "send")
    
    def get_ip_address(self, ifname):
        print_debug("get_ip_address() ifname=%s" %(ifname) )
        if not ifname in netifaces.interfaces():
            return None
        ip=netifaces.ifaddresses(ifname)
        if ip.has_key(netifaces.AF_INET):
            return ip[netifaces.AF_INET][0]['addr']
        return None

    def send_external(self, filenames):
        if self.main.classview.ismultiple():
            if not self.get_all_clients():
                return
        elif not self.get_client():
            return
        # action sent by vidal_joshur at gva dot es
        # send files
        # search for connected users
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg ( _("Can't send files, user is not logged") )
            return
        
        if not os.path.isdir("/tmp/tcos_share"):
            shared.info_msg( _("TcosMonitor: FTP+TLS server is not running.") )
            return
        
        for filename in os.listdir("/tmp/tcos_share/"):
            if os.path.isfile("/tmp/tcos_share/%s" %filename):
                os.remove("/tmp/tcos_share/%s" %filename)
                
        open="True"                                
        basenames = ""
        for filename in filenames:
            basenames += "%s\n" % ( os.path.basename(filename[7:]) )
            copy(filename[7:], "/tmp/tcos_share/")
            os.chmod("/tmp/tcos_share/%s" %os.path.basename(filename[7:]), 0644)
        self.main.write_into_statusbar( _("Waiting for send files...") )
                            
        newusernames=[]
            
        for user in self.connected_users:
            if user.find(":") != -1:
                usern, ip=user.split(":")
                self.main.xmlrpc.newhost(ip)
                server=self.main.xmlrpc.GetStandalone("get_server")
                self.main.xmlrpc.DBus("sendfiles", "%s %s %s" %(_("Teacher"), server, open) )
                self.main.xmlrpc.DBus("mess", _("Teacher has sent some files to %(teacher)s folder:\n\n%(basenames)s")  %{"teacher":_("Teacher"), "basenames":basenames})
            else:
                newusernames.append(user)
                
        interface=self.main.config.GetVar("network_interface")
        # maybe we the x remote display is other than tcosmonitor server
        server=self.get_ip_address(interface)
        result = self.main.dbus_action.do_sendfiles( newusernames , _("Teacher"), server, open)
            
        if not result:
            shared.error_msg ( _("Error while exec remote app:\nReason:%s") %( self.main.dbus_action.get_error_msg() ) )
            self.main.write_into_statusbar( _("Error creating destination folder.") )
        else:
            result = self.main.dbus_action.do_message(newusernames ,
                        _("Teacher has sent some files to %(teacher)s folder:\n\n%(basenames)s") %{"teacher":_("Teacher"), "basenames":basenames} )
            
        self.main.write_into_statusbar( _("Files sent.") )
        

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
            shared.info_msg( _("TcosMonitor: FTP+TLS server is not running.") )
            return
        
        for filename in os.listdir("/tmp/tcos_share/"):
            if os.path.isfile("/tmp/tcos_share/%s" %filename):
                os.remove("/tmp/tcos_share/%s" %filename)
                    
        response = dialog.run()
        
        if response == gtk.RESPONSE_OK:
                            
            filenames = dialog.get_filenames()
            
            open="False"
            basenames = ""
            for filename in filenames:
                basenames += "%s\n" % ( os.path.basename(filename) )
                copy(filename, "/tmp/tcos_share/")
                os.chmod("/tmp/tcos_share/%s" %os.path.basename(filename), 0644)
            self.main.write_into_statusbar( _("Waiting for send files...") )
            
            msg=_( "Do you want open file(s) on client?" )
            if shared.ask_msg ( msg ):
                open="True"
            
            newusernames=[]
            
            for user in self.connected_users:
                if user.find(":") != -1:
                    #usern, ip=user.split(":")
                    #self.main.xmlrpc.newhost(ip)
                    server=self.main.xmlrpc.GetStandalone("get_server")
                    self.main.xmlrpc.DBus("sendfiles", "%s %s %s" %(_("Teacher"), server, open) )
                    self.main.xmlrpc.DBus("mess", _("Teacher has sent some files to %(teacher)s folder:\n\n%(basenames)s")  %{"teacher":_("Teacher"), "basenames":basenames})
                else:
                    newusernames.append(user)
                        
            interface=self.main.config.GetVar("network_interface")
            # maybe we the x remote display is other than tcosmonitor server
            server=self.get_ip_address(interface)
            result = self.main.dbus_action.do_sendfiles( newusernames , _("Teacher"), server, open)
            
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
            shared.info_msg( _("TcosMonitor: FTP+TLS server is not running.") )
            return
        
        for filename in os.listdir("/tmp/tcos_share/"):
            if os.path.isfile("/tmp/tcos_share/%s" %filename):
                os.remove("/tmp/tcos_share/%s" %filename)
                    
        response = dialog.run()
        
        if response == gtk.RESPONSE_OK:
            
            filenames = dialog.get_filenames()
            
            open="False"
            basenames = ""
            for filename in filenames:
                basenames += "%s\n" % ( os.path.basename(filename) )
                copy(filename, "/tmp/tcos_share/")
                os.chmod("/tmp/tcos_share/%s" %os.path.basename(filename), 0644)
            self.main.write_into_statusbar( _("Waiting for send files...") )
            
            msg=_( "Do you want open file(s) on client?" )
            if shared.ask_msg ( msg ):
                open="True"
            
            newusernames=[]
            
            for user in self.connected_users:
                if user.find(":") != -1:
                    usern, ip=user.split(":")
                    self.main.xmlrpc.newhost(ip)
                    server=self.main.xmlrpc.GetStandalone("get_server")
                    self.main.xmlrpc.DBus("sendfiles", "%s %s %s" %(_("Teacher"), server, open) )
                    self.main.xmlrpc.DBus("mess", _("Teacher has sent some files to %(teacher)s folder:\n\n%(basenames)s")  %{"teacher":_("Teacher"), "basenames":basenames})
                else:
                    newusernames.append(user)
                        
            interface=self.main.config.GetVar("network_interface")
            # maybe we the x remote display is other than tcosmonitor server
            server=self.get_ip_address(interface)
            result = self.main.dbus_action.do_sendfiles( newusernames , _("Teacher"), server, open)
            
            if not result:
                shared.error_msg ( _("Error while exec remote app:\nReason:%s") %( self.main.dbus_action.get_error_msg() ) )
                self.main.write_into_statusbar( _("Error creating destination folder.") )
            else:
                result = self.main.dbus_action.do_message(newusernames ,
                            _("Teacher has sent some files to %(teacher)s folder:\n\n%(basenames)s") %{"teacher":_("Teacher"), "basenames":basenames} )
            
            self.main.write_into_statusbar( _("Files sent.") )
        dialog.destroy()


__extclass__=SendFiles
