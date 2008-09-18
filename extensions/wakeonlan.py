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
#import os
import WakeOnLan

def print_debug(txt):
    if shared.debug:
        print "%s::%s" % ("extensions::sendfiles", txt)
    return


class WOL(TcosExtension):
    def register(self):
        self.main.menus.register_simple( _("Boot client (WakeOnLan)") , "menu_wol.png", 0, self.wol_one, "wakeonlan")
        self.main.menus.register_all( _("Boot All clients (WakeOnLan)") , "menu_wol.png", 0, self.wol_all, "wakeonlan")
        

    def wol_one(self, widget, ip):
        if not self.get_client():
            return
        if self.main.config.GetVar("scan_network_method") != "static":
            msg=(_("Wake On Lan only works with static list.\n\nEnable scan method \"static\" in Preferences\nand (wake on lan) support in bios of clients." ))
            shared.info_msg ( msg )
            return
                    
        msg=_( _("Do you want boot %s client?" %ip))
        if shared.ask_msg ( msg ):
            data=[]
            hostslist=self.main.config.GetVar("statichosts")
            #eth=self.main.config.GetVar("network_interface")
            if hostslist == "": return
            data=hostslist.split("#")
            data=data[:-1]
            for host in data:
                mip, mac=host.split("|")
                if mip == self.main.selected_ip:
                    if mac == "":
                        self.main.write_into_statusbar(_("No register MAC address for ip: \"%s\"")%ip)
                        continue
                    print_debug("Send magic packet to mac=%s" %mac)
                    if not WakeOnLan.WakeOnLan("%s"%mac):
                        self.main.write_into_statusbar(_("Not valid MAC address: \"%s\"")%mac)

    def wol_all(self, *args):
        if self.main.config.GetVar("scan_network_method") != "static":
            msg=(_("Wake On Lan only works with static list.\n\nEnable scan method \"static\" in Preferences\nand (wake on lan) support in bios of clients." ))
            shared.info_msg ( msg )
            return
                    
        msg=_( _("Do you want boot all clients?" ))
        if shared.ask_msg ( msg ):
            data=[]
            hostslist=self.main.config.GetVar("statichosts")
            #eth=self.main.config.GetVar("network_interface")
            if hostslist == "": return
            data=hostslist.split("#")
            data=data[:-1]
            errors=[]
            for host in data:
                mac=host.split("|")[1]
                if mac == "":
                    self.main.write_into_statusbar(_("No register MAC address for ip: \"%s\"")%host)
                    continue
                print_debug("Send magic packet to mac=%s" %mac)
                if not WakeOnLan.WakeOnLan("%s"%mac):
                    errors.append(mac)
            if len(errors) >1:
                print_debug("menu_event_all() errors=%s"%errors)
                self.main.write_into_statusbar(_("Not valid MAC address: \"%s\"")%" ".join(errors))


__extclass__=WOL
