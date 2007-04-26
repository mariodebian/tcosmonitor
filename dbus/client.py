#!/usr/bin/python

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
