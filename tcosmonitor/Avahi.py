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
import gobject
import avahi
import avahi.ServiceTypeDatabase
import time
from dbus import DBusException
from dbus.mainloop.glib import DBusGMainLoop

from pprint import pprint


__all__ = ['ZeroconfService', 'AvahiDiscover']



class AvahiDiscover(object):
    def __init__(self, discover_types=['_workstation._tcp'],
                       default_service_name='tcosxmlrpc',
                       loop=None):
        self.services={}
        self.default_service_name=default_service_name
        if loop:
            self.loop
        else:
            self.loop = DBusGMainLoop()
        self.bus = dbus.SystemBus(mainloop=self.loop)
        self.server = dbus.Interface( self.bus.get_object(avahi.DBUS_NAME, '/'),
                                      'org.freedesktop.Avahi.Server')
        
        if len(discover_types)> 0:
            for srv in discover_types:
                self.add_service(srv)
        else:
            for srv in avahi.ServiceTypeDatabase.ServiceTypeDatabase().items():
                self.add_service(srv[0])

    def add_service(self, stype):
        print "add_service() stype=%s"%stype
        sbrowser = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME,
                                                      self.server.ServiceBrowserNew(avahi.IF_UNSPEC,
                                                      avahi.PROTO_INET, stype, 'local', dbus.UInt32(0))),
                                  avahi.DBUS_INTERFACE_SERVICE_BROWSER)
        
        sbrowser.connect_to_signal("ItemNew", self.new_service)
        sbrowser.connect_to_signal('ItemRemove', self.remove_service)

    def mainLoop(self):
        gobject.MainLoop().run()

    def new_service(self, interface, protocol, name, stype, domain, flags):
        if flags & avahi.LOOKUP_RESULT_LOCAL:
                # local service, skip
                return

        self.server.ResolveService(interface, protocol, name, stype, 
            domain, avahi.PROTO_INET, dbus.UInt32(0), 
            reply_handler=self.service_resolved, error_handler=self.print_error)

    def remove_service(self, interface, protocol, name, stype, domain, flags):
        if self.services.has_key(str(name)):
            self.services.pop(str(name))
            self.callback()
        print "------------------------------------------------------------"
        pprint(self.services)
        print "------------------------------------------------------------"
        

    def service_resolved(self, *args):
        service_name=str(args[2])
        if self.default_service_name and not service_name.startswith(self.default_service_name):
            return
        name = args[5].split('.')[0]
        ip = args[7]
        port = args[8]
        txt = args[9]
        #print "NEW hostname=%s ip=%s port=%s TXT=%s"%(name, ip, port, avahi.txt_array_to_string_array(txt))
        self.services[str(args[2])]={'port':int(port), 
                                'ip': str(ip),
                                'hostname':str(name), 
                                'txt':avahi.txt_array_to_string_array(txt),
                                'service_type':str(args[3]),
                                'service_name':str(args[2])}
        print "------------------------------------------------------------"
        pprint(self.services)
        print "------------------------------------------------------------"
        self.callback()

    def print_error(self, *args):
        print 'error_handler'
        print args

    def getConnectedIP(self):
        ips=[]
        for srv in self.services:
            ips.append(self.services[srv]['ip'])
        return ips

    def callback(self):
        pass

    def get_all_ips(self):
        allips=[]
        for srv in self.services:
            allips.append(self.services[srv]['ip'])
        return allips

class ZeroconfService:
    """A simple class to publish a network service with zeroconf using avahi.
        
    Example:
        from ZeroconfService import ZeroconfService
        import time
        
        service = ZeroconfService(name="Joe's awesome FTP server",
                                  port=3000,  stype="_ftp._tcp")
        service.publish()
        time.sleep(10)
        service.unpublish()
    """

    def __init__(self, name, port, stype="_http._tcp",
                 domain="", host="", text=""):
        self.name = name
        self.stype = stype
        self.domain = domain
        self.host = host
        self.port = port
        self.text = text
    
    def publish(self):
        bus = dbus.SystemBus()
        server = dbus.Interface(
                         bus.get_object(
                                 avahi.DBUS_NAME,
                                 avahi.DBUS_PATH_SERVER),
                        avahi.DBUS_INTERFACE_SERVER)

        g = dbus.Interface(
                    bus.get_object(avahi.DBUS_NAME,
                                   server.EntryGroupNew()),
                    avahi.DBUS_INTERFACE_ENTRY_GROUP)

        g.AddService(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC,dbus.UInt32(0),
                     self.name, self.stype, self.domain, self.host,
                     dbus.UInt16(self.port), self.text)

        g.Commit()
        self.group = g
    
    def unpublish(self):
        self.group.Reset()


if __name__ == "__main__":
    #app=AvahiDiscover('_http._tcp', 'tcosxmlrpc')
    app=AvahiDiscover( ['_workstation._tcp', '_http._tcp'] , 'tcos')
    app.mainLoop()
