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
from time import sleep
import sys

from tcosmonitor import shared
from tcosmonitor.TcosExtensions import TcosExtension


def print_debug(txt):
    if shared.debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)


class iTalc(TcosExtension):
    def register(self):
        self.main.menus.register_simple( _("Connect to remote screen (iTALC)"), "menu_remote.png", 1, self.ivs, "italc")
        

    def ivs(self, w, ip):
        if not self.get_client():
            return
        
        if len(self.allclients_logged) == 0:
            shared.error_msg( _("No user logged.") )
            return
        
        self.main.worker=shared.Workers(self.main, target=self.start_ivs, args=(self.allclients_logged) )
        self.main.worker.start()

    def start_ivs(self, ip):
        self.main.xmlrpc.newhost(ip)
        # check if remote proc is running
        if not self.main.xmlrpc.GetStatus("ivs"):
            self.main.common.threads_enter("TcosActions:start_ivs write connecting msg")
            self.main.write_into_statusbar( "Connecting with %s to start iTALC support" %(ip) )
            self.main.common.threads_leave("TcosActions:start_ivs write connecting msg")
            
            try:
                self.main.xmlrpc.newhost(ip)
                self.main.xmlrpc.Exe("startivs")
                self.main.common.threads_enter("TcosActions:start_ivs write waiting msg")
                self.main.write_into_statusbar( "Waiting for start of IVS server..." )
                self.main.common.threads_leave("TcosActions:start_ivs write waiting msg")
                sleep(5)
            except Exception, err:
                print_debug("start_ivs() Exception, error=%s"%err)
                self.main.common.threads_enter("TcosActions:start_ivs write error msg")
                shared.error_msg ( _("Can't start IVS, please add iTALC support") )
                self.main.common.threads_leave("TcosActions:start_ivs write error msg")
                return
                
        cmd = "icv " + ip + " root"
        print_debug ( "start_process() threading \"%s\"" %(cmd) )
        self.main.common.exe_cmd (cmd, verbose=0, background=True)
        
        self.main.common.threads_enter("TcosActions:start_ivs END")
        self.main.write_into_statusbar( "" )
        self.main.common.threads_leave("TcosActions:start_ivs END")

__extclass__=iTalc






