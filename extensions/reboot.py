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

import shared
from TcosExtensions import TcosExtension


def print_debug(txt):
    if shared.debug:
        print "%s::%s" %("extensions::reboot", txt)
    return


class RebootPoweroff(TcosExtension):
    def register(self):
        self.main.menus.register_simple(_("Reboot"), "menu_reboot.png", 0, self.reboot)
        self.main.menus.register_all( _("Reboot all clients"), "menu_reboot.png", 0, self.reboot_all)
        self.main.menus.register_simple( _("Poweroff"), "menu_poweroff.png", 0, self.poweroff)
        self.main.menus.register_all( _("Poweroff all clients"), "menu_poweroff.png", 0, self.poweroff_all)

    def reboot(self, w, ip):
        if not self.get_client():
            return
        msg=_( _("Do you want to reboot %s?" ) %(self.host) )
        if shared.ask_msg ( msg ):
            timeout=self.main.config.GetVar("actions_timeout")
            msg=(_("Pc will reboot in %s seconds") %timeout)
            self.exe_app_in_client("reboot", timeout, msg, users=[ip], connected_users=self.connected_users)
    

    def reboot_all(self, *args):
        if not self.get_all_clients():
            return
        msg=_( _("Do you want to reboot the following hosts:%s?" ) %(self.allclients_txt) )
        if shared.ask_msg ( msg ):
            timeout=self.main.config.GetVar("actions_timeout")
            msg=(_("Pc will reboot in %s seconds") %timeout)
            self.exe_app_in_client("reboot", timeout, msg, users=self.allclients, connected_users=self.connected_users)

    def poweroff(self, w, ip):
        if not self.get_client():
            return
        msg=_( _("Do you want to poweroff %s?" ) %(self.host) )
        if shared.ask_msg ( msg ):
            timeout=self.main.config.GetVar("actions_timeout")
            msg=(_("Pc will shutdown in %s seconds") %timeout)
            self.exe_app_in_client("poweroff", timeout, msg, users=[ip], connected_users=self.connected_users)
    

    def poweroff_all(self, *args):
        if not self.get_all_clients():
            return
        msg=_( _("Do you want to poweroff the following hosts:%s?" )%(self.allclients_txt) )
        if shared.ask_msg ( msg ):
            timeout=self.main.config.GetVar("actions_timeout")
            msg=(_("Pc will shutdown in %s seconds") %timeout)
            self.exe_app_in_client("poweroff", timeout, msg, users=self.allclients, connected_users=self.connected_users)

    def real_action(self, ip, action):
        print_debug("real_action() ip=%s action='%s'"%(ip,action) )
        self.main.xmlrpc.Exe(action)


    def exe_app_in_client(self, mode, timeout=0, msg="", users=[], connected_users=[]):
        remote_cmd=("/usr/lib/tcos/session-cmd-send %s %s %s" %(mode.upper(), timeout, msg.replace("'", "´")))
        action="down-controller %s %s" %(mode, timeout)
        print_debug("exe_app_in_client() usernames=%s" %users)
        
        if len(connected_users) != 0 and connected_users[0] != shared.NO_LOGIN_MSG:
            newusernames=[]
            for user in connected_users:
                if user.find(":") != -1:
                    # we have a standalone user...
                    usern, ip = user.split(":")
                    self.main.xmlrpc.newhost(ip)
                    self.main.xmlrpc.DBus("exec", remote_cmd )
                else:
                    # we have a thin client
                    newusernames.append(user)
                                
            result = self.main.dbus_action.do_exec( newusernames ,remote_cmd )
                
            if not result:
                shared.error_msg ( _("Error while exec remote app:\nReason:%s") %( self.main.dbus_action.get_error_msg() ) )
        
        self.main.worker=shared.Workers(self.main, None, None)
        self.main.worker.set_for_all_action(self.action_for_clients, users, action )
        return




__extclass__=RebootPoweroff






