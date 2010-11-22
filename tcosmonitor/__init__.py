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

import glob as __glob__
import os   as __os__
import sys  as __sys__

def __load__():
    """
    read contents of tcosmonitor dir and put in __all__ list
    """
    _ext_dir=__os__.path.dirname( __file__ )
    _ext=[]
    for file_ in __glob__.glob(_ext_dir+"/*.py"):
        if file_ == "__init__.py":
            continue
        _ext_name = __os__.path.basename(file_).split('.py')[0]
        if _ext_name == "__init__":
            continue
        _ext.append( _ext_name )
        try:
            if __sys__.version_info[0:3] < (2, 5, 0):
                __import__('tcosmonitor.' + _ext_name, globals(), locals(), ['extensions'] ) 
            else:
                __import__('tcosmonitor.' + _ext_name, fromlist = ['extensions'] ) 
        except Exception, err:
            print ("Exception importing tcosmonitor='%s', err='%s'"%(_ext_name, err))
    return _ext


if not "DISPLAY" in __os__.environ or __os__.environ['DISPLAY'] == '':
    print >> __sys__.stderr, ("WARNING: [tcosmonitor.__init__] No display defined, no importing extensions")
else:
    if "TCOSMONITOR_NO_EXTENSIONS" in __os__.environ:
        print >> __sys__.stderr, ("TCOSMONITOR_NO_EXTENSIONS in environment, no load extensions")
    else:
        __all__=__load__()
