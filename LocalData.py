# -*- coding: UTF-8 -*-
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

import shared

import popen2
import os
from gettext import gettext as _
from time import time
from ping import *

COL_HOST, COL_IP, COL_USERNAME, COL_ACTIVE, COL_LOGGED, COL_BLOCKED, COL_PROCESS, COL_TIME = range(8)



unknow=_("unknow")


def print_debug(txt):
    if shared.debug:
        print "%s::%s" %(__name__, txt)
        
def crono(start, txt):
    print_debug ("crono(), %s get %f seconds" %(txt, (time() - start)) )
    return



class LocalData:
    def __init__(self, main):
        print_debug ( "__init__()" )
        self.main=main
        self.allclients=None
        self.allclients=[]
        self.dhostname=_("unknow")
        self.hostname=None
        self.username=None
        self.ip=None
        self.active=None
        self.logged=None
        self.blocked=None
        self.num_process=None
        self.time_login=None
        self.allhostdata=[]
        #self.cache_timeout=shared.cache_timeout
        self.cache_timeout=self.main.config.GetVar("cache_timeout")
    
    def newhost(self, host):
        print_debug ( "newhost(%s)" %(host) )
        self.hostname=None
        self.ip=host
        self.username=None
        self.active=None
        self.logged=None
        self.blocked=None
        self.num_process=None
        self.time_login=None
    
    def cache(self, ip, num):
        """
        cache array is like this:
            self.allhostdata [ ip, hostname, username, numprocess() , timelogged() , isLogged(bool), time() ]
                                0      1        2         3              4              5              6
        """
        print_debug ( "cache(ip=\"%s\" [ %s ])" %(ip, num) )
        for i in range(len(self.allhostdata)):
            if self.allhostdata[i][0] == ip:
                print_debug ( "cache() %s cached from %s secs" %(ip, float(time() - self.allhostdata[i][6])) )
                if time() - self.allhostdata[i][6] < self.cache_timeout:
                    print_debug ( "cache() IS CACHED" )
                    print_debug ( "cache() %s" %(self.allhostdata[i]) )
                    return self.allhostdata[i][num]
                else:
                    #clean cache
                    print_debug ( "cache() DELETE OLD CACHE" )
                    print_debug ( self.allhostdata )
                    self.allhostdata.pop(i)
                    print_debug ( self.allhostdata )
                    return None
        #print_debug ( "\n%s\n" %(self.allhostdata) )
        return None
        
    def add_to_cache(self, ip, num, value):
        print_debug ( "add_to_cache(\"%s\", \"%s\", \"%s\")" %(ip, num, value) )
        
        if self.cache(ip, num) != None:
            print_debug ( "add_to_cache() already cached" )
            return
        
        new=True
        for host in self.allhostdata:
            if host[0] == ip:
                new=False
        
        if new:
            self.allhostdata.append( [ip, None, None, None, None, None, time() ] )
        
        for i in range(len(self.allhostdata)):
            if self.allhostdata[i][0] == ip:
                if self.allhostdata[i][num] == value:
                    if time() - self.allhostdata[i][6] < self.cache_timeout:
                        print_debug ( "cached at %s secs" %(float(time() - self.allhostdata[i][6])) )
                        return
                # save value in num pos
                #print_debug ( "add_to_cache(%s)[%d]=%s EDIT HOST" %(ip, num, value) )
                self.allhostdata[i][num]=value
                self.allhostdata[i][6]=time()
        
        #print_debug ( self.allhostdata )
    
    def exe_cmd(self, cmd, verbose=1):
        output=[]
        (stdout, stdin) = popen2.popen2(cmd)
        stdin.close()
        for line in stdout:
            if line != '\n':
                line=line.replace('\n', '')
                output.append(line)
        if len(output) == 1:
            return output[0]
        elif len(output) > 1:
            if verbose==1:
                print_debug ( "get_result(%s) %s" %(cmd, output) )
            return output
        else:
            if verbose == 1:
                print_debug ( "get_result(%s)=None" %(cmd) )
            return []
        
    def GetAllClients(self, method):
        """
        Read active connections at 6000 local port
        OTHER BEST METHOD??? "who" ???
        read netstat -putan|grep 6000|awk '{print $5}'| awk -F ":" '{print $2}| sort|uniq'
        """
        
        if method == "ping":
            interface=self.main.config.GetVar("network_interface")
            print_debug ( "GetAllClients() using method \"ping\" in interface %s" %(interface) )
            """
            ping=Ping(self.main)
            ss=ping.get_ip_address(interface)
            dd=ping.ping_iprange(ss)
            return dd
            """
            ping=Ping(self.main)
            ss=ping.get_ip_address(interface)
            
            print_debug ( "GetAllClients() method=ping starting worker without dog" )
            self.main.worker=shared.Workers(self.main, ping.ping_iprange, [ss], dog=False )
            self.main.worker.start()
            
            return []
            
        else:
            print_debug ( "GetAllClients() using method \"netstat\" in port 600[0-9]" )
            start=time()
            self.allclients=[]
            self.hostname=None
            #read this command output
            #cmd="netstat -putan 2>/dev/null | grep \":6000\"| awk '{print $5}'"
            cmd="netstat -putan 2>/dev/null | grep  \":600[0-9] \"| grep ESTABLISHED | awk '{print $5}'"
            #print_debug ( "GetAllClients() exec=\"%s\"" %(cmd) )
            #(stdout, stdin) = popen2.popen2(cmd)
            #stdin.close()
            #output = stdout.readlines()
            output=self.exe_cmd(cmd)
            for xhost in output:
                host=xhost.split(':', 1)[0]
                if host != "" and host != "0.0.0.0" and host != "127.0.0.1":
                    if host not in self.allclients:
                        self.allclients.append(host)
            # sort list
            self.allclients.sort()
        
            print_debug ( "GetAllClients() Host connected=%s" %(self.allclients) )
            crono(start, "GetAllClients()")
            return self.allclients

    
    def ipValid(self, ip):
        # ip is XXX.XXX.XXX.XXX
        # http://mail.python.org/pipermail/python-list/2006-March/333963.html
        
        try:
            xip=ip.split('.')
            if len(xip) != 4:
                print_debug ( "ipValid() len != 4" )
                return false
            for block in xip:
                if int(block) < 0 or int(block) >= 255:
                    print_debug ( "ipValid() block < 0 or >= 255 %s" %(block) )
                    return false
            print_debug ( "ipValid(\"%s\") TRUE" %(ip) )
            return True
        except:
            print_debug ( "ipValid(\"%s\") EXCEPTION" %(ip) )
            return False
        
        
    def GetHostname(self, ip):
        """
        Try to resolve ip to hostname
           first read /etc/hosts
           second search into dhcpd.conf
        """
        ########  cache( ip, 1=hostname)
        cached=self.cache(ip, 1)
        if cached != None:
            return cached
            
        start=time()
        #if self.hostname != None:
        #    return self.hostname
        
        self.hostname=unknow
        
        #read hostnam from /etc/hosts
        fd=file("/etc/hosts", 'r')
        allfile=fd.read()
        allfile=allfile.split('\n')
        fd.close()
        print_debug ( "GetHostname() searching ip=%s" %(ip) )
        for line in allfile:
            if line.find('#')==0:
                continue
            if line.find(' ')==0:
                continue
            if len(line) == 0:
                continue
            
            # split cuts with '\t' or ' '
            xline=line.split()    
            
            print_debug ( "xline=%s" %(xline) )
            if self.ipValid(xline[0]):
                if xline[0]==ip and len(xline) == 2:
                    self.hostname = xline[1]
                    self.add_to_cache( ip, 1 , self.hostname )
                    return self.hostname
            
            
        print_debug ( "GetHostname() search in /etc/hosts no results, try DHCP leases """ )
        
        #search in dhcpd.conf if /etc/dhcp3/dhcpd.conf exists
        if not os.path.isfile("/etc/dhcp3/dhcpd.conf"):
            print_debug ( "GetHostname() /etc/dhcp3/dhcpd.conf not found" )
            crono(start, "GetHostname()")
            # save into cache
            self.add_to_cache( ip, 1 , self.hostname )
            return self.hostname
        else:
            cmd="grep -A 3 -B 3 \"fixed.*%s;\" /etc/dhcp3/dhcpd.conf|grep -v \"^#\"|grep host|awk '{print $2}'" %(ip)
            print_debug ( "GetHostname(%s) cmd=\"%s\"" %(ip, cmd) )
            (stdout, stdin) = popen2.popen2(cmd)
            stdin.close()
            output = stdout.readlines()
            if len(output) > 1:
                print_debug ( "GetHostname() DHCP have many leases=%s" %(output) )
                crono(start, "GetHostname()")
                # save into cache
                self.add_to_cache( ip, 1 , self.hostname )
                return self.hostname
                
            elif len(output) == 0:
                print_debug ( "GetHostname() DHCP not found enter" )
                crono(start, "GetHostname()")
                # save into cache
                self.add_to_cache( ip, 1 , self.hostname )
                return self.hostname
                
            else:
                for lease in output:
                    self.hostname=lease.replace('\n', '')
                    print_debug ( "GetHostname() found DHCP hostname=%s for ip=%s" %(self.hostname,ip) )
                    crono(start, "GetHostname()")
                    # save into cache
                    self.add_to_cache( ip, 1 , self.hostname )
                    return self.hostname
                    
        crono(start, "GetHostname()")
        # save into cache
        self.add_to_cache( ip, 1 , self.hostname )
        return self.hostname

    def GetUsername(self, ip):
        """
        read username
        """
        ########  cache( ip, 1=hostname)
        # FIXME esto falla mas que una escopeta de feria
        #cached=self.cache(ip, 2)
        #if cached != None:
        #    print_debug ( "GetUsername() RETURNING CACHE DATA" )
        #    return cached
            
        #if self.username != None:
        #    return self.username
        
        self.username=shared.NO_LOGIN_MSG
        
        if not self.IsActive(ip):
            print_debug ( "GetUsername(%s) not active, returning NO_LOGIN_MSG" %(ip) )
            return shared.NO_LOGIN_MSG
        
        cmd="who |grep \"%s \" | head -1 |awk '{print $1}'" %(ip)
        output=self.exe_cmd(cmd)
        if output != []:
            self.username=output
            self.add_to_cache( ip, 2 , self.username )
            return self.username
        
        
        cmd="who |grep \"%s \" | head -1 |awk '{print $1}'" %( self.GetHostname(ip) )
        output=self.exe_cmd(cmd)
        if output != []:
            self.username=output
            self.add_to_cache( ip, 2 , self.username )
            return self.username
        
        print_debug ( "GetUsername() fail to search username, return unknow" )
        self.add_to_cache( ip, 2 , self.username )
        return self.username
        
    def IsActive(self, host):
        """
        return True or False if host is active
        use xmlrpc echo
        """
        print_debug ( "IsActive(%s) = %s " %(host, self.main.xmlrpc.GetVersion()) )
        if self.main.xmlrpc.GetVersion() != None:
            print_debug ( "IsActive(%s)=True" %(host) )
            return True
        else:
            print_debug ( "IsActive(%s)=False" %(host) )
            return False

    def IsLogged(self, host):
        """
        return True if is logged
        """
        if self.GetUsername(host) != shared.NO_LOGIN_MSG:
            return True
        else:
            return False
            
    def IsBlocked(self, host):
        """
        return if lockscreen is exec
        """
        self.main.xmlrpc.newhost(host)
        if self.main.xmlrpc.status_lockscreen() == 1:
            return True
        else:
            return False

    def GetNumProcess(self, host):
        """
        return number of process
        """
        self.username=self.GetUsername(host)
        
        if self.username == None:
            return "---"
        
            
        if self.username == shared.NO_LOGIN_MSG:
            return "---"
        
        #cmd=" ps aux|grep \"^%s \"| wc -l" %(self.username)
        cmd=" ps aux|grep -c \"^%s \"" %(self.username)
        print_debug ("GetNumProcess() exec=%s" %(cmd) )
        process=self.exe_cmd(cmd)
        
        print_debug ("GetNumProcess() process=%s" %(process) )
        return process
    
    
        
    def GetTimeLogged(self, host):
        #if self.username == None:
        #    self.username=self.GetUsername(host)
        #
        if self.username == shared.NO_LOGIN_MSG:
            return "---"

        
        # get date
        #cmd="LANG=C date +'%F %H:%M'"
        
        last=None
        
        cmd="LC_ALL=C LANGUAGE=C LANG=C date +'%b %d %H:%M'"
        date=self.exe_cmd(cmd)
        
        cmd="LC_ALL=C LANGUAGE=C LANG=C who| awk '{print $1\"|\"$2\"|\"$3\" \"$4\" \"$5}'"
        allhost=self.exe_cmd(cmd)
        # get an array like this ['username'|'hostname or IP:0'|'Jul 12 21:56']

        for line in allhost:
            xhost=line.split('|')
            if xhost[1] == "%s:0" %(host):
                last=xhost[2]
            if xhost[1] == "%s:0" %(self.GetHostname(host)):
                last=xhost[2]
        
        print_debug ("TimeLogged() last=%s date=%s" %(last, date) )
        # FORMAT AAAA-MM-DD HH:MM compare
        if last==date or last==None:
            return "00:00"
            
        (monthlast, daylast, hourlast) = last.split(' ')
        (monthdate, daydate, hourdate) = date.split(' ')
        if int(daylast) != int(daydate):
            print_debug ("GetTimeLogged() Login another day daylast=%s daylate=%s!!!!" %(daylast,daydate))
        (hlast, mlast)= hourlast.split(':')
        (hdate, mdate)= hourdate.split(':')
        #restar
        hlogged=int(hdate) - int(hlast)
        mlogged=int(mdate) - int(mlast)
        print_debug ("TimeLogged() DIFF user=%s date=%s" %(hourlast, hourdate) )
        hdays=""
        if mlogged < 1:
            hlogged=hlogged-1
            mlogged=mlogged+60
        if hlogged < 0:
            hdays="1d "
            hlogged=hlogged+24
        print_debug ("TimeLogged() hour=%02d minute=%02d" %(hlogged, mlogged) )
        return "%s%02d:%02d" %(hdays, hlogged, mlogged)
        
if __name__ == '__main__':
    local=LocalData (None)
    local.GetAllClients()
    local.GetHostname("192.168.0.2")
    local.GetHostname("192.168.0.10")
    local.GetUsername("192.168.0.10")
    local.GetTimeLogged("192.168.0.10")
