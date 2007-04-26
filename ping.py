# -*- encoding: UTF-8 -*-
#  Based on 
# Filename: ping.py
# Discripion:
# Author(s): yetist
# Version:
# URL: http://www.osprg.org/modules/newbb/viewtopic.php?forum=3&post_id=487

import os
import re
from threading import Thread
import socket
import fcntl
import struct
from gettext import gettext as _

if "DISPLAY" in os.environ:
    if os.environ["DISPLAY"] != "":
        import gtk


import shared

def print_debug(txt):
    if shared.debug:
        print "%s::%s" %(__name__, txt)

class pingip(Thread):
   def __init__ (self,ip):
      Thread.__init__(self)
      self.ip = ip
      self.status = -1
      self.lifeline = re.compile(r"(\d) received")
   def run(self):
      #print_debug ( "pingip() %s" %(self.ip) )
      pingaling = os.popen("ping -q -W 1 -c2 "+self.ip,"r")
      while 1:
        line = pingaling.readline()
        if not line: break
        igot = re.findall(self.lifeline,line)
        if igot:
            self.status = int(igot[0])

class Ping:
    def __init__(self, main):
        print_debug ( "__init__()" )
        self.main=main
        self.reachip=[]

    def ping_iprange(self, selfip):
        pinglist = []
        reachip =[]
        for i in range(1,255):
            iprange=selfip.split(".")[:-1]
            ip=".".join(iprange)+"."+str(i)
            #print "ping to %s" %(ip)
            if self.main.worker.is_stoped():
                # this is a stop thread var
                break
            ##########
            gtk.gdk.threads_enter()
            self.main.progressbar.show()
            self.main.progressbutton.show()
            self.main.actions.set_progressbar( _("Ping to %s...") \
                            %(ip), float(i)/float(254) )
            gtk.gdk.threads_leave()
            ############
            current = pingip(ip)
            pinglist.append(current)
            current.start()
        
        gtk.gdk.threads_enter()
        self.main.actions.set_progressbar( _("Waiting for pings...") , float(1) )
        gtk.gdk.threads_leave()
     
        for pingle in pinglist:
            pingle.join()
            if pingle.status == 2:
                reachip.append(pingle.ip)
        
        self.main.worker.set_finished()
        
        if len(reachip) == 0:
            gtk.gdk.threads_enter()
            self.main.write_into_statusbar ( _("No host found") )
            self.main.progressbar.hide()
            self.main.progressbutton.hide()
            gtk.gdk.threads_enter()
        
        if len(reachip) > 0:
            gtk.gdk.threads_enter()
            self.main.write_into_statusbar ( _("Found %d hosts" ) %len(reachip) )
            gtk.gdk.threads_leave()
            
            self.main.localdata.allclients=reachip
            
            self.main.worker=shared.Workers( self.main,\
                     target=self.main.actions.populate_hostlist, args=([reachip]) )
            self.main.worker.start()
            
        return reachip
 
    def get_ip_address(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])

##########################################################################
# TcosMonitor writen by MarioDebian <mariodebian@gmail.com>
#
#
# Copyright (c) 2006 Mario Izquierdo <mariodebian@gmail.com>
# All rights reserved.
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

class PingPort:
    """ try to open a socket to host:ip """
    def __init__(self, host, port, timeout=1):
        self.host=host
        self.port=int(port)
        if self.host == "":
            print_debug ( "PingPort()  need host to connect" )
            self.status = "CLOSED"
            return
        
        self.status=None
        socket.setdefaulttimeout(timeout)
        self.sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print_debug( "PingPort()::__init__(host=%s, port=%d timeout=%f)" %(self.host, self.port, timeout) )        
        try:
            # connect to the given host:port
	        self.sd.connect((host, port))
        except socket.error:
            # set the CLOSED flag
            self.status = "CLOSED"
        else:
            self.status = "OPEN"
            self.sd.close()

        import shared
        socket.setdefaulttimeout(timeout)

    def get_status(self):
        """ return socket status
            values: OPEN CLOSED
        """
        print_debug ( "%s:%s port is \"%s\"" %(self.host, self.port, self.status) )
        import shared
        socket.setdefaulttimeout(shared.socket_default_timeout)
        return self.status


if __name__ == '__main__':
    #for i in range(20):
    #    PingPort("192.168.0.3", i+100).get_status()
    PingPort("192.168.0.5", 6000, 0.5).get_status()
    PingPort("192.168.0.1", 6000, 0.5).get_status()
    PingPort("192.168.0.3", 6000, 0.5).get_status()
