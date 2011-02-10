#!/usr/bin/env python
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

import dbus
import dbus.service
import dbus.glib
import gobject
import os
import signal
import subprocess
import pwd

username = pwd.getpwuid(os.getuid())[0]
print "username=%s" %(username)

bus = dbus.SystemBus()
#remote_object = bus.get_object("com.consoltux.TcosMonitor", "/SCPObject")
#iface = dbus.Interface(remote_object, "com.consoltux.TcosMonitor.Comm")

def new_message(message):
   print "new_message=%s" %(message)
   for user in message[0]:
	if user == username:
	    if message[1][0] == "kill":
		os.kill(int(message[2][0]), signal.SIGKILL)
	    if message[1][0] == "exec":
		subprocess.Popen(message[2][0], shell=True)
	    if message[1][0] == "mess":
		subprocess.Popen(['zenity', '--info', '--text=' + message[2][0] + ' ', '--title="Message from admin"'])

#iface.connect_to_signal('hello_signal', new_message)

bus.add_signal_receiver(new_message,
                        signal_name='GotSignal',
                        dbus_interface='com.consoltux.TcosMonitor.Comm',
                        path='/TCOSObject')

#bus.add_signal_receiver(new_message,
#                        'DeviceAdded',
#                        'org.freedesktop.Hal.Manager',
#                        'org.freedesktop.Hal',
#                        '/org/freedesktop/Hal/Manager')

mainloop = gobject.MainLoop()
mainloop.run()
