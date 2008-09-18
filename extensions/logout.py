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
#from TcosExtensions import TcosExtension, Error
from TcosExtensions import TcosExtension


def print_debug(txt):
    if shared.debug:
        print "%s::%s" % ("extensions::logout", txt)
    return


class LogOut(TcosExtension):
    def register(self):
        self.main.menus.register_simple( _("Logout client"),  "menu_restartx.png", 0, self.logout, "restartx")
        self.main.menus.register_all( _("Logout clients"), "menu_restartx.png" , 0, self.logout_all, "restartx")
        

    def logout(self, w, ip):
        if not self.get_client():
            return
        msg=_( _("Do you want to logout user \"%s\"?" ) %(self.connected_users[0]) )
        if shared.ask_msg ( msg ):
            newusernames=[]
            timeout=self.main.config.GetVar("actions_timeout")
            msg=_("Session will close in %s seconds") %timeout
            remote_cmd="/usr/lib/tcos/session-cmd-send LOGOUT %s %s" %(timeout, msg.replace("'", "´"))
            
            if self.connected_users[0].find(":") != -1:
                # we have a standalone user...
                self.main.xmlrpc.DBus("exec", remote_cmd )
            else:
                newusernames.append(self.connected_users[0])
                    
            self.main.dbus_action.do_exec(newusernames, remote_cmd )

    def logout_all(self, widget):
        if not self.get_all_clients():
            return
        msg=_( _("Do you want to logout the following users:%s?" )%(self.newallclients_txt) )
        if shared.ask_msg ( msg ):
            newusernames=[]
            timeout=self.main.config.GetVar("actions_timeout")
            msg=_("Session will close in %s seconds") %timeout
            remote_cmd="/usr/lib/tcos/session-cmd-send LOGOUT %s %s" %(timeout, msg.replace("'", "´"))
            
            for user in self.connected_users:
                if user.find(":") != -1:
                    # we have a standalone user...
                    usern, ip = user.split(":")
                    self.main.xmlrpc.newhost(ip)
                    self.main.xmlrpc.DBus("exec", remote_cmd )
                else:
                    newusernames.append(user)
                        
            self.main.dbus_action.do_exec( newusernames, remote_cmd )

__extclass__=LogOut






