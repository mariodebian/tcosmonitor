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

def print_debug(txt):
    if shared.debug:
        print "%s::%s" % ("extensions::tcosnetcontroller", txt)
    return


class TcosNetController(TcosExtension):
    def register(self):
        self.main.menus.register_simple( _("Lock internet"), "menu_locknet.png", 1, self.locknet_simple, "net")
        self.main.menus.register_simple( _("Unlock internet"), "menu_unlocknet.png", 1, self.unlocknet_simple, "net")
        
        self.main.menus.register_all( _("Lock internet in all connected users"), "menu_locknet.png", 1, self.locknet_all, "net")
        self.main.menus.register_all( _("Unlock internet in all connected users"), "menu_unlocknet.png", 1, self.unlocknet_all, "net")

    def locknet_simple(self, w, ip):
        if not self.get_client():
            return
        # lock net
        eth=self.main.config.GetVar("network_interface")
        ports="--ports=%s" %self.main.config.GetVar("ports_tnc")
        remote_msg=_("Internet connection has been disabled")
        act="disable-internet"
        
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg ( _("Can't disable internet, user is not logged") )
            return
        
        if self.client_type == "tcos":
            if not self.main.localdata.user_in_group(None, 'tcos'):
                msg=(_("In order to lock and unlock internet you need to be in 'tcos' group.\n\nExe by root: adduser %s tcos" ) %(self.main.localdata.get_username()))
                shared.error_msg ( msg )
                return
            result = self.main.localdata.BlockNet(act, self.connected_users[0], ports, eth)
            if result == "disabled":
                self.main.dbus_action.do_message( self.connected_users, remote_msg )
        else:
            result = self.main.xmlrpc.tnc(act, self.connected_users[0].split(":")[0], ports)
            if result == "disabled":
                self.main.xmlrpc.DBus("mess", remote_msg)
        
        self.change_lockscreen(ip)


    def unlocknet_simple(self, w, ip):
        if not self.get_client():
            return
        # unlock net
        remote_msg=_("Internet connection has been enabled")
        act="enable-internet"
        
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg ( _("Can't enable internet, user is not logged") )
            return
        if self.client_type == "tcos":
            if not self.main.localdata.user_in_group(None, 'tcos'):
                msg=(_("In order to lock and unlock internet you need to be in 'tcos' group.\n\nExe by root: adduser %s tcos" ) %(self.main.localdata.get_username()))
                shared.error_msg ( msg )
                return
            result = self.main.localdata.BlockNet(act, self.connected_users[0])
            if result == "enabled":
                self.main.dbus_action.do_message( self.connected_users, remote_msg )
        else:
            result = self.main.xmlrpc.tnc(act, self.connected_users[0].split(":")[0])
            if result == "enabled":
                self.main.xmlrpc.DBus("mess", remote_msg)
        
        self.change_lockscreen(ip)


    def locknet_all(self, *args):
        if not self.get_all_clients():
            return
        if not self.main.localdata.user_in_group(None, 'tcos'):
            msg=(_("In order to lock and unlock internet you need to be in 'tcos' group.\n\nExe by root: adduser %s tcos" ) %(self.main.localdata.get_username()))
            shared.error_msg ( msg )
            return
        # disable internet
        eth=self.main.config.GetVar("network_interface")
        ports="--ports=%s" %self.main.config.GetVar("ports_tnc")
        remote_msg=_("Internet connection has been disabled")
        act="disable-internet"
        
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg( _("No users logged.") )
            return
        
        msg=_( _("Do you want disable internet to following users: %s?" )%(self.connected_users_txt) )
                                                
        if not shared.ask_msg ( msg ):
            return
        
        newusernames=[]
            
        for user in self.connected_users:
            if user.find(":") != -1:
                usern, ip=user.split(":")
                self.main.xmlrpc.newhost(ip)
                result = self.main.xmlrpc.tnc(act, usern, ports)
                if result == "disabled":
                    self.main.xmlrpc.DBus("mess", remote_msg)
            else:
                result = self.main.localdata.BlockNet(act, user, ports, eth)
                if result == "disabled":
                    newusernames.append(user)
                
        result = self.main.dbus_action.do_message( newusernames, remote_msg )
        
        for client in self.newallclients:
            self.main.localdata.newhost(client)
            self.main.xmlrpc.newhost(client)
            self.change_lockscreen(client)


    def unlocknet_all(self, *args):
        if not self.get_all_clients():
            return
        if not self.main.localdata.user_in_group(None, 'tcos'):
            msg=(_("In order to lock and unlock internet you need to be in 'tcos' group.\n\nExe by root: adduser %s tcos" ) %(self.main.localdata.get_username()))
            shared.error_msg ( msg )
            return
        # enable internet
        remote_msg=_("Internet connection has been enabled")
        act="enable-internet"
        
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg( _("No users logged.") )
            return
        
        msg=_( _("Do you want enable internet to following users:%s?" )%(self.newallclients_txt) )
                                                
        if not shared.ask_msg ( msg ):
            return
        
        newusernames=[]
            
        for user in self.connected_users:
            if user.find(":") != -1:
                usern, ip=user.split(":")
                self.main.xmlrpc.newhost(ip)
                result = self.main.xmlrpc.tnc(act, usern)
                if result == "enabled":
                    self.main.xmlrpc.DBus("mess", remote_msg)
            else:
                result = self.main.localdata.BlockNet(act, user)
                if result == "enabled":
                    newusernames.append(user)
                
        result = self.main.dbus_action.do_message( newusernames, remote_msg )
        
        for client in self.newallclients:
            self.main.localdata.newhost(client)
            self.main.xmlrpc.newhost(client)
            self.change_lockscreen(client)


__extclass__=TcosNetController






