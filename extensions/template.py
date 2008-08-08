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

extension_name="Info Extension"
__main__=None
__name__=extension_name

import shared

def print_debug(txt):
    if shared.debug:
        print "%s::%s" %("extensions::info", txt)
    return

def __register__(main=None):
    print_debug( "__register__()" )
    if main:
        global __main__
        __main__=main
        #__main__.common.get_icon_theme()

def __init__():
    print_debug( "__init__()" )
    print main()

def __run__():
    print_debug( "__run__()" )

def main():
    global __main__
    return __main__

# functions or class that init/run extension
extension_register=__register__
extension_init=__init__
extension_run=__run__




