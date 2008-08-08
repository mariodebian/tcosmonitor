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
        print "%s::%s" %("extensions::clean", txt)
    return


class Clean(TcosExtension):
    def register(self):
        self.main.menus.register_simple(_("Clean info about terminal"), "menu_clear.png", 0, self.clean)
        self.main.menus.register_all( _("Clean info about terminal"), "menu_clear.png", 0, self.clean)

    def clean(self, *args):
        print_debug("clean()")
        self.main.datatxt.clean()
        self.main.write_into_statusbar('')
    





__extclass__=Clean








