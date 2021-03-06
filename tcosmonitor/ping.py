# -*- coding: UTF-8 -*-
#
#  pingip based on 
#   Filename: ping.py
#    Discripion:
#    Author(s): yetist
#    Version:
#    URL: http://www.osprg.org/modules/newbb/viewtopic.php?forum=3&post_id=487
#
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



import sys
import os
import re
from threading import Thread
import socket
from gettext import gettext as _
from subprocess import Popen, PIPE, STDOUT

import netifaces
import IPy
import tcosmonitor.shared

import xml.dom.minidom

def print_debug(txt):
    if tcosmonitor.shared.debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)

class pingip(Thread):
    def __init__ (self, ip):
        Thread.__init__(self)
        self.ip = ip
        self.status = -1
        self.lifeline = re.compile(r"(\d) received")
    def run(self):
        #print_debug("ping to '%s'" %self.ip)
        pingalingout = Popen(["ping", "-q", "-W1", "-c2", "%s" %self.ip], \
                shell=False, stdout=PIPE, stderr=STDOUT, close_fds=True)
        try:
            pingalingout.wait()
        except Exception, err:
            print_debug("pingip() Exception in wait() error: %s"%err)
        pingaling = pingalingout.stdout
        while 1:
            line = pingaling.readline()
            if not line:
                break
            igot = re.findall(self.lifeline, line)
            if igot:
                self.status = int(igot[0])

class Ping:
    def __init__(self, main):
        print_debug ( "__init__()" )
        self.main=main
        self.reachip=[]

    def ping_iprange_nmap(self, selfip):
        print_debug("ping_iprange_nmap() ip=%s"%selfip)
        pinglist=[]
        reachip=[]
        
        server_ips=self.get_server_ips()
        self.main.common.threads_enter("Nmap:only show tcos")
        self.main.write_into_statusbar( _("Testing if found clients have 8998 or 8999 port open..."))
        self.main.common.threads_leave("Nmap:only show tcos")
        
        if self.main.config.GetVar("onlyshowtcos") == 1:
            print_debug("cmd='nmap -sS -p%s -n --open -oX - %s'"%(tcosmonitor.shared.xmlremote_port, selfip))
            cmd="nmap -sS -p%s -n --open -oX - %s" %(tcosmonitor.shared.xmlremote_port, selfip)
        else:
            print_debug("cmd='nmap -sP -n -oX - %s'"%selfip)
            cmd="nmap -sP -n -oX - %s" %selfip
            
        try:
            p = Popen(cmd, shell=True, bufsize=100000, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
        except Exception, e:
            print_debug("Exception in subprocess cmd(%s), error='%s'"%(cmd, e))
            return None
            
        # Use dom to parse output, idea taken from python-nmap source   
        # wait until finished
        # get output
        (nmap_last_output, nmap_err) = p.communicate()
        # If there was something on stderr, there was a problem so abort...
        if len(nmap_err) > 0:
            print_debug("Error in nmap cmd(%s), error='%s'"%(cmd, nmap_err))
            return []
            
        dom = xml.dom.minidom.parseString(nmap_last_output)
        
        for dhost in  dom.getElementsByTagName('host'):
            ipnmap = dhost.getElementsByTagName('address')[0].getAttributeNode('addr').value
            for dstatus in dhost.getElementsByTagName('status'):
                # is up?
                up = dstatus.getAttributeNode('state').value
                reason = dstatus.getAttributeNode('reason').value
            if up != "up" or reason != "arp-response":
                continue
            if self.main.config.GetVar("onlyshowtcos") == 1:
                for dport in dhost.getElementsByTagName('port'):
                    proto = dport.getAttributeNode('protocol').value
                    port =  int(dport.getAttributeNode('portid').value)
                    state = dport.getElementsByTagName('state')[0].getAttributeNode('state').value
                    if port == tcosmonitor.shared.xmlremote_port and state == "open":
                        pinglist.append(ipnmap)
            else:
                pinglist.append(ipnmap)
                
        print_debug(pinglist)
        try:
            inhosttcos=str(tcosmonitor.shared.parseIPAddress(os.environ["DISPLAY"]))
                # running tcosmonitor on thin client ?
        except Exception, err:
            print_debug("ping_iprange_nmap() can't read DISPLAY, %s"%err)
            
        i=0
        for ipnmap in pinglist:
            i=i+1
            if ipnmap in server_ips:
                print_debug("Nmap:: ip (%s) is in server_ips(%s)" % (ipnmap, server_ips) )
                continue
            #print "ping to %s" %(ip)
            if self.main.worker.is_stoped():
                print_debug("ping_iprange_nmap() WORKER is stoped")
                # this is a stop thread var
                break
            ##########
            self.main.common.threads_enter("Ping:ping_iprange_nmap show progress")
            self.main.progressbar.show()
            self.main.progressbutton.show()
            self.main.actions.set_progressbar( _("Checking %s...")%(ipnmap), float(i)/len(pinglist) )
            #print_debug("ping_iprange() ip=%s"%(ip))
            self.main.common.threads_leave("Ping:ping_iprange_nmap show progress")
            ############

                # check for notshowwhentcosmonitor
            if self.main.config.GetVar("notshowwhentcosmonitor") == 1:
                # if $DISPLAY = xx.xx.xx.xx:0 remove from allclients
                if inhosttcos == ipnmap:
                        # running tcosmonitor on thin client
                        continue
                
            # only show in list hosts running tcosxmlrpc in 8998 or 8999 port
            if self.main.config.GetVar("onlyshowtcos") == 1:
                self.main.common.threads_enter("Ping:only show tcos")
                self.main.write_into_statusbar( _("Testing if found clients have 8998 or 8999 port open..."))
                self.main.common.threads_leave("Ping:only show tcos")
                # view status of port 8998 or 8999
                if self.main.xmlrpc.newhost(ipnmap):
                    if self.main.xmlrpc.GetVersion():
                        print_debug("ping_iprange() host=%s ports 8998 or 8999 OPEN" %(ipnmap))
                        reachip.append(ipnmap)
                    else:
                        print_debug("ping_iprange() host=%s ports 8998 or 8999 OPEN but not tcosxmlrpc" %(ipnmap))
                else:
                    print_debug("ping_iprange() host=%s ports 8998 or 8999 closed" %(ipnmap))
            else:
                reachip.append(ipnmap)
        
        print_debug("ping_iprange_nmap() discovered host finished" )
        self.main.worker.set_finished()
        
        if len(reachip) == 0:
            self.main.common.threads_enter("Ping:ping_iprange_nmap print no hosts")
            self.main.write_into_statusbar ( _("Not connected hosts found.") )
            self.main.progressbar.hide()
            self.main.progressbutton.hide()
            self.main.common.threads_leave("Ping:ping_iprange_nmap print no hosts")
        
        if len(reachip) > 0:
            self.main.common.threads_enter("Ping:ping_iprange_nmap print num hosts")
            self.main.actions.lenclients=len(reachip)
            self.main.write_into_statusbar ( _("Found %d hosts" ) %len(reachip) )
            self.main.common.threads_leave("Ping:ping_iprange_nmap print num hosts")
            
            self.main.localdata.allclients=reachip
            
            self.main.worker=tcosmonitor.shared.Workers( self.main,\
                     target=self.main.actions.populate_hostlist, \
                     args=([reachip]) )
            self.main.worker.start()
            
        return reachip
        
    def ping_iprange(self, selfip):
        print_debug("ping_iprange() ip=%s"%selfip)
        pinglist=[]
        reachip=[]
        server_ips=self.get_server_ips()
            
        for i in range(1, 255):
            iprange=selfip.split(".")[:-1]
            ip=".".join(iprange)+"."+str(i)
            # don't show server in list
            if ip in server_ips:
                print_debug("Ping:: ip (%s) is in server_ips(%s)" % (ip, server_ips) )
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
            try:
                # in some situations ( I can reproduce ) thread can't be started
                # don't fail and only wait if thread start ok
                current.start()
                pinglist.append(current)
            except Exception, err:
                print_debug("ping thread Exception ip=%s err=%s"%(ip, err))
        
        self.main.common.threads_enter("Ping:ping_iprange print waiting")
        self.main.actions.set_progressbar( _("Waiting for pings...") , float(1) )
        self.main.common.threads_leave("Ping:ping_iprange print waiting")
     
        try:
            inhosttcos=str(tcosmonitor.shared.parseIPAddress(os.environ["DISPLAY"]))
                # running tcosmonitor on thin client ?
        except Exception, err:
            print_debug("ping_iprange_nmap() can't read DISPLAY, %s"%err)
            
        for pingle in pinglist:
            pingle.join()
            if pingle.status == 2:
                # check for notshowwhentcosmonitor
                if self.main.config.GetVar("notshowwhentcosmonitor") == 1:
                    # if $DISPLAY = xx.xx.xx.xx:0 remove from allclients
                    if inhosttcos == pingle.ip:
                        # running tcosmonitor on thin client
                        continue
                
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
            self.main.write_into_statusbar ( _("Not connected hosts found.") )
            self.main.progressbar.hide()
            self.main.progressbutton.hide()
            self.main.common.threads_leave("Ping:ping_iprange print no hosts")
        
        if len(reachip) > 0:
            self.main.common.threads_enter("Ping:ping_iprange print num hosts")
            self.main.actions.lenclients=len(reachip)
            self.main.write_into_statusbar ( _("Found %d hosts" ) %len(reachip) )
            self.main.common.threads_leave("Ping:ping_iprange print num hosts")
            
            self.main.localdata.allclients=reachip
            
            self.main.worker=tcosmonitor.shared.Workers( self.main,\
                     target=self.main.actions.populate_hostlist, \
                     args=([reachip]) )
            self.main.worker.start()
            
        return reachip
    
    
    def ping_iprange_static(self, allclients):
        print_debug("ping_iprange_static() ip=%s"%allclients)
        pinglist=[]
        reachip=[]
            
        for ip in allclients:
            #print "ping to %s" %(ip)
            if self.main.worker.is_stoped():
                print_debug("ping_iprange() WORKER is stoped")
                # this is a stop thread var
                break
            current = pingip(ip)
            pinglist.append(current)
            current.start()
     
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
        
        print_debug("ping_iprange_static() discovered host finished" )
        self.main.worker.set_finished()

        self.main.localdata.allclients=reachip
        
        if len(reachip) == 0:
            self.main.common.threads_enter("Ping:ping_iprange_static print no hosts")
            self.main.write_into_statusbar ( _("Not connected hosts found.") )
            self.main.common.threads_leave("Ping:ping_iprange_static print no hosts")
        
        if len(reachip) > 0:
            self.main.common.threads_enter("Ping:ping_iprange_static print num hosts")
            self.main.write_into_statusbar ( _("Found %d hosts" ) %len(reachip) )
            self.main.common.threads_leave("Ping:ping_iprange_static print num hosts")
                        
            self.main.worker=tcosmonitor.shared.Workers( self.main,\
                     target=self.main.actions.populate_hostlist, \
                     args=([reachip]) )
            self.main.worker.start()
            
        return reachip
 
    def get_ip_address(self, ifname):
        print_debug("get_ip_address() ifname=%s" %(ifname) )
        if not ifname in netifaces.interfaces():
            return None
        ip=netifaces.ifaddresses(ifname)
        if ip.has_key(netifaces.AF_INET):
            return ip[netifaces.AF_INET][0]['addr']
        return None

    def get_net_address(self, ifname):
        print_debug("get_net_address() ifname=%s" %(ifname) )
        if not ifname in netifaces.interfaces():
            return None
        ip=netifaces.ifaddresses(ifname)
        if ip.has_key(netifaces.AF_INET):
            address="%s" %ip[netifaces.AF_INET][0]['addr']
            mask="%s" %ip[netifaces.AF_INET][0]['netmask']
            net="%s" %IPy.IP(address).make_net(mask)
            print_debug("net=%s" %net)
            return net
        return None
        
    def get_server_ips(self):
        IPS=[]
        for dev in netifaces.interfaces():
            if not dev in tcosmonitor.shared.hidden_network_ifaces:
                print_debug("get_server_ips() add interface %s"%dev)
                ip=netifaces.ifaddresses(dev)
                if ip.has_key(netifaces.AF_INET):
                    ip[netifaces.AF_INET][0]['gateway']=self.get_gateway(dev)
                    print_debug("get_server_ips() iface=%s data=%s"%(dev, ip[netifaces.AF_INET] ))
                    IPS.append(ip[netifaces.AF_INET][0]['addr'])
        return IPS

    def get_gateway(self, iface):
        data=[]
        f=open("/proc/net/route", 'r')
        for l in f.readlines():
            if l.startswith(iface):
                tmp=l.strip().split()
                if tmp[1] == "00000000":
                    data.append(self.__hex2dec__(tmp[2]))
        f.close()
        if len(data) < 1:
            #print ("WARNING: no gateway")
            return None
        else:
            return data[0]

    def __hex2dec__(self, s):
        out=[]
        for i in range(len(s)/2):
            out.append( str(int(s[i*2:(i*2)+2], 16)) )
        # data in /proc/net/route is reversed
        out.reverse()
        return ".".join(out)


class PingPort:
    """ try to open a socket to host:ip """
    def __init__(self, host, port, timeout=1):
        self.host=host
        self.port=int(port)
        print_debug("PingPort() host=%s port=%d" %(host, self.port) )
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
        
        socket.setdefaulttimeout(timeout)

    def get_status(self):
        """ return socket status
            values: OPEN CLOSED
        """
        print_debug ( "%s:%s port is \"%s\"" %(self.host, self.port, self.status) )
        socket.setdefaulttimeout(tcosmonitor.shared.socket_default_timeout)
        return self.status


if __name__ == '__main__':
    tcosmonitor.shared.debug=True
    #for i in range(20):
    #    PingPort("192.168.0.3", i+100).get_status()
    #PingPort("192.168.0.5", 6000, 0.5).get_status()
    #PingPort("192.168.0.1", 6000, 0.5).get_status()
    #PingPort(sys.argv[1], sys.argv[2], 0.5).get_status()
    app=Ping(None)
    print ( app.get_server_ips() )
    print ( app.get_ip_address('eth0') )
    print ( app.get_ip_address('br0') )
    
