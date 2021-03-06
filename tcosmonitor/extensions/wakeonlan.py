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
import sys

from tcosmonitor import shared
from tcosmonitor.TcosExtensions import TcosExtension

from tcosmonitor.WakeOnLan import WakeOnLan

def print_debug(txt):
    if shared.debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)


class WOL(TcosExtension):
    def register(self):
        self.main.menus.register_simple( _("Boot client (WakeOnLan)") , "menu_wol.png", 0, self.wol_one, "wakeonlan")
        self.main.menus.register_all( _("Boot All clients (WakeOnLan)") , "menu_wol.png", 0, self.wol_all, "wakeonlan")
        

    def wol_one(self, widget, ip):
        if not self.get_client():
            print_debug("wol_one() no client")
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
            if hostslist == "":
                return
            data=hostslist.split("#")
            data=data[:-1]
            for host in data:
                mip, mac=host.split("|")
                print_debug("wol_one() ip=%s mac=%s" %(mip, mac) )
                if mip == self.main.selected_ip:
                    if mac == "":
                        self.main.write_into_statusbar(_("No register MAC address for ip: \"%s\"")%ip)
                        continue
                    print_debug("Send magic packet to mac=%s" %mac)
                    if not WakeOnLan("%s"%mac):
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
            if hostslist == "":
                return
            data=hostslist.split("#")
            data=data[:-1]
            errors=[]
            for host in data:
                mac=host.split("|")[1]
                if mac == "":
                    self.main.write_into_statusbar(_("No register MAC address for ip: \"%s\"")%host)
                    continue
                print_debug("Send magic packet to mac=%s" %mac)
                if not WakeOnLan("%s"%mac):
                    errors.append(mac)
            if len(errors) >1:
                print_debug("menu_event_all() errors=%s"%errors)
                self.main.write_into_statusbar(_("Not valid MAC address: \"%s\"")%" ".join(errors))


__extclass__=WOL
