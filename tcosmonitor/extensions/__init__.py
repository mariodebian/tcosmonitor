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

import glob as __glob__
import os   as __os__
import sys  as __sys__

def __load__():
    """
    read contents of extensions dir and put in __all__ list
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
                __import__('tcosmonitor.extensions.' + _ext_name, globals(), locals(), ['extensions'] ) 
            else:
                __import__('tcosmonitor.extensions.' + _ext_name, fromlist = ['extensions'] ) 
        except Exception, err:
            print ("Exception importing extension='%s', err='%s'"%(_ext_name, err))
    return _ext

__all__=__load__()
