# -*- encoding: UTF-8 -*-
#  pingip based on 
#   Filename: ping.py
#    Discripion:
#    Author(s): yetist
#    Version:
#    URL: http://www.osprg.org/modules/newbb/viewtopic.php?forum=3&post_id=487
#
# 


import os
import sys
import re
from threading import Thread
import socket
import fcntl
import struct
from gettext import gettext as _
from time import sleep
from subprocess import Popen, PIPE, STDOUT

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
      #pingaling = self.main.common.exe_cmd("ping -q -W1 -c2 %s" %self.ip, verbose=0, background=False, lines=1)
      pingalingout = Popen(["ping", "-q", "-W1", "-c2", "%s" %self.ip], shell=False, stdout=PIPE, stderr=STDOUT, close_fds=True)
      try:
          pingalingout.wait()
      except Exception, err:
          print_debug("pingip() Exception in wait() error: %s"%err)
      pingaling = pingalingout.stdout
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
        print_debug("ping_iprange() ip=%s"%selfip)
        pinglist = []
        reachip =[]
        server_ips=self.get_server_ips()
            
        for i in range(1,255):
            iprange=selfip.split(".")[:-1]
            ip=".".join(iprange)+"."+str(i)
            # don't show server in list
            if ip in server_ips:
                continue
            #print "ping to %s" %(ip)
            if self.main.worker.is_stoped():
                print_debug("ping_iprange() WORKER is stoped")
                # this is a stop thread var
                break
            ##########
            self.main.common.threads_enter("Ping:ping_iprange show progress")
            self.main.progressbar.show()
            self.main.progressbutton.show()
            self.main.actions.set_progressbar( _("Ping to %s...")%(ip), float(i)/float(254) )
            #print_debug("ping_iprange() ip=%s"%(ip))
            self.main.common.threads_leave("Ping:ping_iprange show progress")
            ############
            current = pingip(ip)
            pinglist.append(current)
            current.start()
        
        self.main.common.threads_enter("Ping:ping_iprange print waiting")
        self.main.actions.set_progressbar( _("Waiting for pings...") , float(1) )
        self.main.common.threads_leave("Ping:ping_iprange print waiting")
     
        for pingle in pinglist:
            pingle.join()
            if pingle.status == 2:
                # only show in list hosts running tcosxmlrpc in 8998 or 8999 port
                if self.main.config.GetVar("onlyshowtcos") == 1:
                    self.main.common.threads_enter("Ping:only show tcos")
                    self.main.write_into_statusbar( _("Testing if found clients have 8998 or 8999 port open..."))
                    self.main.common.threads_leave("Ping:only show tcos")
                    # view status of port 8998 or 8999
                    if self.main.xmlrpc.newhost(pingle.ip):
                        if self.main.xmlrpc.GetVersion():
                            print_debug("ping_iprange() host=%s ports 8998 or 8999 OPEN" %(pingle.ip))
                            reachip.append(pingle.ip)
                        else:
                            print_debug("ping_iprange() host=%s ports 8998 or 8999 OPEN but not tcosxmlrpc" %(pingle.ip))
                    else:
                        print_debug("ping_iprange() host=%s ports 8998 or 8999 closed" %(pingle.ip))
                else:
                    reachip.append(pingle.ip)
        
        print_debug("ping_iprange() discovered host finished" )
        self.main.worker.set_finished()
        
        if len(reachip) == 0:
            self.main.common.threads_enter("Ping:ping_iprange print no hosts")
            self.main.write_into_statusbar ( _("No host found") )
            self.main.progressbar.hide()
            self.main.progressbutton.hide()
            self.main.common.threads_leave("Ping:ping_iprange print no hosts")
        
        if len(reachip) > 0:
            self.main.common.threads_enter("Ping:ping_iprange print num hosts")
            self.main.write_into_statusbar ( _("Found %d hosts" ) %len(reachip) )
            self.main.common.threads_leave("Ping:ping_iprange print num hosts")
            
            self.main.localdata.allclients=reachip
            
            self.main.worker=shared.Workers( self.main,\
                     target=self.main.actions.populate_hostlist, args=([reachip]) )
            self.main.worker.start()
            
        return reachip
 
    def get_ip_address(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            ip=socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', ifname[:15])
            )[20:24])
        except Exception, err:
            ip=None
            print_debug("get_ip_address() ifname %s don't have ip address, error=%s"%(ifname,err))
        return ip


    def get_server_ips(self):
        IPS=[]
        for dev in os.listdir("/sys/class/net"):
            if not dev in shared.hidden_network_ifaces:
                print_debug ( "get_server_ips() add interface %s" %dev )
                ip=self.get_ip_address(dev)
                if ip:
                    print_debug("appending ip %s"%ip)
                    IPS.append(ip)
               
        print_debug("get_server_ips() IPS=%s"%IPS)
        return IPS


##########################################################################
# TcosMonitor writen by MarioDebian <mariodebian@gmail.com>
#
# TcosMonitor version __VERSION__
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

class PingPort:
    """ try to open a socket to host:ip """
    def __init__(self, host, port, timeout=1):
        self.host=host
        self.port=int(port)
        print_debug("PingPort() host=%s port=%d" %(host,self.port) )
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
	        self.sd.connect((self.host, self.port))
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
    shared.debug=True
    #for i in range(20):
    #    PingPort("192.168.0.3", i+100).get_status()
    #PingPort("192.168.0.5", 6000, 0.5).get_status()
    #PingPort("192.168.0.1", 6000, 0.5).get_status()
    PingPort(sys.argv[1], sys.argv[2], 0.5).get_status()
    #app=Ping(None)
    #print app.get_server_ips()
