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
import os
import sys

from tcosmonitor import shared
from tcosmonitor.TcosExtensions import TcosExtension

def print_debug(txt):
    if shared.debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)


class TcosPersonalize(TcosExtension):
    def register(self):
        self.main.menus.register_simple( _("Configure this host"), "menu_configure.png", 0, self.launch_tcospersonalize, "personalize")
        

    def launch_tcospersonalize(self, w, ip):
        if not self.get_client():
            return
        if self.client_type == "tcos":
            if self.main.ingroup_tcos == False and os.getuid() != 0:
                cmd="gksu \"tcospersonalize --host=%s\"" %(ip)
            else:
                cmd="tcospersonalize --host=%s" %(ip)
            print_debug ( "launch_tcospersonalize() cmd=%s" %(cmd) )
            th=self.main.common.exe_cmd( cmd, verbose=0, background=True )
        else:
            shared.info_msg( _("%s is not supported to personalize!") %(self.client_type) )



__extclass__=TcosPersonalize






