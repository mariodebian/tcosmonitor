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
from TcosExtensions import TcosExtension, Error


def print_debug(txt):
    if shared.debug:
        print "%s::%s" %("extensions::lockscreen", txt)
    return


class LockUnlockScreen(TcosExtension):
    def register(self):
        self.main.menus.register_simple( _("Lock screen"), "menu_lock.png", 0, self.lock)
        self.main.menus.register_all( _("Lock all screens"), "menu_lock.png", 0, self.lock_all)
        self.main.menus.register_simple( _("Unlock screen"), "menu_unlock.png", 0, self.unlock)
        self.main.menus.register_all( _("Unlock all screens"), "menu_unlock.png", 0, self.unlock_all)

    def lock(self, w, ip):
        if not self.get_client():
            return
        if not self.main.xmlrpc.lockscreen():
            shared.error_msg( _("Can't connect to tcosxmlrpc.\nPlease verify user and password in prefences!") )
            return
        self.change_lockscreen(ip)

    def unlock(self, w, ip):
        if not self.get_client():
            return
        if not self.main.xmlrpc.unlockscreen():
            shared.error_msg( _("Can't connect to tcosxmlrpc.\nPlease verify user and password in prefences!") )
            return
        self.change_lockscreen(ip)

    def real_action(self, ip, action):
        print_debug("real_action() ip=%s action='%s'"%(ip,action) )
        
        if action == 'lockscreen':
            self.main.xmlrpc.lockscreen()
            # update icon
            self.main.common.threads_enter("TcosActions::action_for_clients lockscreen")
            self.change_lockscreen(ip)
            self.main.common.threads_leave("TcosActions::action_for_clients lockscreen")
        elif action == 'unlockscreen':
            self.main.xmlrpc.unlockscreen()
            # update icon
            self.main.common.threads_enter("TcosActions::action_for_clients unlockscreen")
            self.change_lockscreen(ip)
            self.main.common.threads_leave("TcosActions::action_for_clients unlockscreen")


    def lock_all(self, *args):
        if not self.get_all_clients():
            return
        msg=_( _("Do you want to lock the following screens:%s?" )%(self.allclients_logged_txt) )
        if shared.ask_msg ( msg ):
            self.main.worker=shared.Workers(self.main, None, None)
            self.main.worker.set_for_all_action(self.action_for_clients,\
                                                 self.allclients_logged, "lockscreen" )

    def unlock_all(self, *args):
        if not self.get_all_clients():
            return
        msg=_( _("Do you want to unlock the following screens:%s?" )%(self.allclients_logged_txt) )
        if shared.ask_msg ( msg ):
            self.main.worker=shared.Workers(self.main, None, None)
            self.main.worker.set_for_all_action(self.action_for_clients,\
                                                self.allclients_logged, "unlockscreen" )


__extclass__=LockUnlockScreen






