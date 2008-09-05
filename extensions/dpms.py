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
        print "%s::%s" %("extensions::dpms", txt)
    return


class Dpms(TcosExtension):
    def register(self):
        self.main.menus.register_simple( _("DPMS Power off monitor"), "menu_dpms_off.png", 0, self.dpms_off)
        self.main.menus.register_all( _("DPMS Power off monitors"), "menu_dpms_off.png", 0, self.dpms_off_all)
        self.main.menus.register_simple( _("DPMS Power on monitor"), "menu_dpms_on.png", 0, self.dpms_on)
        self.main.menus.register_all( _("DPMS Power on monitors"), "menu_dpms_on.png", 0, self.dpms_on_all)

    def dpms_off(self, w, ip):
        if not self.get_client():
            return
        # DPMS off
        self.main.xmlrpc.dpms('off')
        self.change_lockscreen(self.main.selected_ip)

    def dpms_on(self, w, ip):
        if not self.get_client():
            return
        # DPMS on
        self.main.xmlrpc.dpms('on')
        self.change_lockscreen(self.main.selected_ip)

    def real_action(self, ip, action):
        print_debug("real_action() ip=%s action='%s'"%(ip,action) )
        
        if action == 'dpmsoff':
            result=self.main.xmlrpc.dpms('off')
            print_debug("real_action() DPMS OFF result=%s"%result)
            self.main.common.threads_enter("extensions/dpms::real_action dpms off")
            self.change_lockscreen(ip)
            self.main.common.threads_leave("extensions/dpms::real_action dpms off")
        elif action == 'dpmson':
            result=self.main.xmlrpc.dpms('on')
            print_debug("real_action() DPMS ON result=%s"%result)
            self.main.common.threads_enter("extensions/dpms::real_action dpms on")
            self.change_lockscreen(ip)
            self.main.common.threads_leave("extensions/dpms::real_action dpms on")


    def dpms_off_all(self, *args):
        if not self.get_all_clients():
            return
        msg=_( _("Do you want to switch off the following monitors:%s?" ) %(self.allclients_logged_txt) )
        if shared.ask_msg ( msg ):
            self.main.worker=shared.Workers(self.main, None, None)
            self.main.worker.set_for_all_action(self.action_for_clients,\
                                                 self.allclients_logged, "dpmsoff" )

    def dpms_on_all(self, *args):
        if not self.get_all_clients():
            return
        msg=_( _("Do you want to switch on the following monitors:%s?" ) %(self.allclients_logged_txt) )
        if shared.ask_msg ( msg ):
            self.main.worker=shared.Workers(self.main, None, None)
            self.main.worker.set_for_all_action(self.action_for_clients,\
                                                 self.allclients_logged, "dpmson" )


__extclass__=Dpms






