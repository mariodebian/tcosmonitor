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
        print "%s::%s" % ("extensions::remotessh", txt)
    return


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






