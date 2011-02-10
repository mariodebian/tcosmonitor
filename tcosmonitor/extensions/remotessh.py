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


def print_debug(txt):
    if shared.debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)


class RemoteSSH(TcosExtension):
    def register(self):
        self.main.menus.register_simple( _("Give a remote xterm"), "menu_xterm.png", 0, self.remotessh, "shell")
        

    def remotessh(self, w, ip):
        if not self.get_client():
            return
        # give a remote xterm throught SSH
        pass_msg=_("Enter password of remote thin client (if asked for it)")
        cmd="xterm -e \"echo '%s'; ssh %s@%s || sleep 5\"" %(pass_msg, self.main.config.GetVar("ssh_remote_username"),ip)
        print_debug ( "remotessh() cmd=%s" %(cmd) )
        th=self.main.common.exe_cmd( cmd, verbose=0, background=True )



__extclass__=RemoteSSH






