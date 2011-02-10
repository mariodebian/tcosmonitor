#!/usr/bin/python
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
#
#  Based on StudentControlPanel of Ubuntu
#
#

import signal
#import gobject
#import pwd
#import subprocess
import dbus
import dbus.service
import dbus.glib

class SCPObject(dbus.service.Object):

    def __init__(self, bus_name, object_path="/TCOSObject"):
        dbus.service.Object.__init__(self, bus_name, object_path)

    @dbus.service.signal("com.consoltux.TcosMonitor.Comm", signature="aas")
    def GotSignal(self, message):
        pass


system_bus = dbus.SystemBus()
name = dbus.service.BusName("com.consoltux.TcosMonitor", bus=system_bus)
dbus_iface = SCPObject(name)

dbus_iface.GotSignal([ ["mario"] , ["exec"] , ["xterm"] ])
dbus_iface.GotSignal([ ["mario"] , ["mess"] , ["Test message from dbus interface"] ])
