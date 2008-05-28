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

import shared

import os
from gettext import gettext as _
from time import time, ctime, localtime
from ping import *

import utmp
from UTMPCONST import *

import pwd,grp

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
        if self.main:
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
        #print_debug ( "cache(ip=\"%s\" [ %s ])" %(ip, num) )
        for i in range(len(self.allhostdata)):
            if self.allhostdata[i][0] == ip:
                #print_debug ( "cache() %s cached from %s secs" %(ip, float(time() - self.allhostdata[i][6])) )
                if time() - self.allhostdata[i][6] < self.cache_timeout:
                    #print_debug ( "cache() IS CACHED" )
                    #print_debug ( "cache() %s" %(self.allhostdata[i]) )
                    return self.allhostdata[i][num]
                else:
                    #clean cache
                    #print_debug ( "cache() DELETE OLD CACHE" )
                    #print_debug ( self.allhostdata )
                    self.allhostdata.pop(i)
                    print_debug ( self.allhostdata )
                    return None
        #print_debug ( "\n%s\n" %(self.allhostdata) )
        return None
        
    def add_to_cache(self, ip, num, value):
        print_debug ( "add_to_cache(\"%s\", \"%s\", \"%s\")" %(ip, num, value) )
        
        if self.cache(ip, num) != None:
            #print_debug ( "add_to_cache() already cached" )
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

    def get_username(self):
        return pwd.getpwuid(os.getuid())[0]

    def get_userid(self):
        return os.getuid()

    def user_in_group(self, user=None, group=None):
        #tcos.libs.conf.debug_enabled=True
        if not user:
            user=self.get_username()
        sgroups=grp.getgrall()
        if user == "root":
            return True
        for (sgroup, spass, sid, susers) in sgroups:
            if sgroup == group and user in susers:
                print_debug("user %s is in group %s"%(user, sgroup), console.name(__name__) )
                return True
        return False
    
    def sorted_copy(self, alist):
        # inspired by Alex Martelli
        # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52234
        indices = map(self._generate_index, alist)
        decorated = zip(indices, alist)
        decorated.sort()
        return [ item for index, item in decorated ]
    
    def _generate_index(self, str):
        """
        Splits a string into alpha and numeric elements, which
        is used as an index for sorting"
        """
        #
        # the index is built progressively
        # using the _append function
        #
        index = []
        def _append(fragment, alist=index):
            if fragment.isdigit(): fragment = int(fragment)
            alist.append(fragment)

        # initialize loop
        prev_isdigit = str[0].isdigit()
        current_fragment = ''
        # group a string into digit and non-digit parts
        for char in str:
            curr_isdigit = char.isdigit()
            if curr_isdigit == prev_isdigit:
                current_fragment += char
            else:
                _append(current_fragment)
                current_fragment = char
                prev_isdigit = curr_isdigit
        _append(current_fragment)    
        return tuple(index)

        
    def GetAllClients(self, method):
        """
        Read active connections at 6000 local port
        OTHER BEST METHOD??? "who" ???
        read netstat -putan|grep 6000|awk '{print $5}'| awk -F ":" '{print $2}| sort|uniq'
        """
        
        if method == "ping":
            interface=self.main.config.GetVar("network_interface")
            print_debug ( "GetAllClients() using method \"ping\" in interface %s" %(interface) )
            
            ping=Ping(self.main)
            ss=ping.get_ip_address(interface)
            if ss == None:
                self.main.write_into_statusbar( _("Selected network inteface (%s) don't have IP address" ) %(interface) )
                return []
            print_debug ( "GetAllClients() method=ping starting worker without dog iface=%s ip=%s" %(interface,ss) )
            self.main.worker=shared.Workers(self.main, ping.ping_iprange, [ss], dog=False )
            self.main.worker.start()
            
            return []
            
        elif method == "netstat":
            print_debug ( "GetAllClients() using method \"netstat\" in port 600[0-9]" )
            start=time()
            self.allclients=[]
            self.hostname=None
            #read this command output
            cmd="LC_ALL=C LC_MESSAGES=C netstat -putan 2>/dev/null | grep  \":600[0-9] \"| grep ESTABLISHED | awk '{print $5}'"
            
            output=self.main.common.exe_cmd(cmd)
            
            #avoid to have a spimple string
            if type(output) == type(""):
                output=[output]
            
            for xhost in output:
                host=xhost.split(':', 1)[0]
                if host != "" and host != "0.0.0.0":
                    if host not in self.allclients:
                        #print(host)
                        self.allclients.append(host)
            # sort list
            self.allclients.sort()
            
            # sort numeric
            self.allclients = self.sorted_copy(self.allclients)
            
            # onlys show host running tcosxmlrpc in 8998 port
            if self.main.config.GetVar("onlyshowtcos") == 1:
                if hasattr(self.main, "write_into_statusbar"):
                    self.main.write_into_statusbar( _("Testing if found clients have %s port open...") %(shared.xmlremote_port) )
                hosts=[]
                for host in self.allclients:
                    # view status of port 8998
                    if PingPort(host, shared.xmlremote_port, 0.5).get_status() == "OPEN":
                        self.main.xmlrpc.newhost(host)
                        if self.main.xmlrpc.GetVersion():
                            print_debug("GetAllClients() host=%s port 8998 OPEN" %(host))
                            hosts.append(host)
                        else:
                            print_debug("GetAllClients() host=%s port 8998 OPEN but not tcosxmlrpc" %(host))
                    else:
                        print_debug("GetAllClients() host=%s port 8998 CLOSED" %(host))
                        hosts.append(host)
                self.allclients=hosts
            
            print_debug ( "GetAllClients() Host connected=%s" %(self.allclients) )
            crono(start, "GetAllClients()")
            return self.allclients
        else:
            self.allclients=[]
            if len(self.main.static.data) < 1:
                shared.error_msg( _("Static list method configured but no hosts in list.\n\nPlease, open preferences, click on 'Open Static Host list' and add some hosts.") )
                return self.allclients
                
            for host in self.main.static.data:
                # we have a single ip or range of ips??
                ip=host[0]
                if ip.find("-") != -1:
                    base=ip.split(".")
                    minip=int(base[3].split("-")[0])
                    maxip=int(base[3].split("-")[1])
                    if minip < maxip:
                        for i in range(minip,maxip):
                            newip=".".join(base[0:3]) + ".%s" %(i)
                            self.allclients.append(newip)
                    else:
                        for i in range(maxip, minip):
                            newip=".".join(base[0:3]) + ".%s" %(i)
                            self.allclients.append(newip)
                else:
                    self.allclients.append(ip)
            # try if client is connected
            if self.main.config.GetVar("onlyshowtcos") == 1:
                if hasattr(self.main, "write_into_statusbar"):
                    self.main.write_into_statusbar( _("Testing if found clients have %s port open...") %(shared.xmlremote_port) )
                hosts=[]
                for host in self.allclients:
                    # view status of port 8998
                    if PingPort(host, shared.xmlremote_port, 0.5).get_status() == "OPEN":
                        self.main.xmlrpc.newhost(host)
                        if self.main.xmlrpc.GetVersion():
                            print_debug("GetAllClients() host=%s port 8998 OPEN" %(host))
                            hosts.append(host)
                        else:
                            print_debug("GetAllClients() host=%s port 8998 OPEN but not tcosxmlrpc" %(host))
                    else:
                        print_debug("GetAllClients() host=%s port 8998 CLOSED" %(host))
                        #hosts.append(host)
                self.allclients=hosts
                print_debug("GetAllClients() returning static list %s"%self.allclients)
            return self.allclients

    
    def ipValid(self, ip):
        # ip is XXX.XXX.XXX.XXX
        # http://mail.python.org/pipermail/python-list/2006-March/333963.html
        
        try:
            xip=ip.split('.')
            if len(xip) != 4:
                #print_debug ( "ipValid() len != 4" )
                return False
            for block in xip:
                if int(block) < 0 or int(block) >= 255:
                    print_debug ( "ipValid() block < 0 or >= 255 %s" %(block) )
                    return False
            return True
        except:
            return False

    def GetIpAddress(self, hostname):
        try:
            return socket.getaddrinfo(hostname, None)[0][4][0]  
        except:
            return None
        
    def GetHostname(self, ip):
        """
        Try to resolve ip to hostname
           first read /etc/hosts
           second search into dhcpd.conf
        """
        print_debug("GetHostname() ip=%s" %(ip))
        ########  cache( ip, 1=hostname)
        cached=self.cache(ip, 1)
        if cached != None:
            return cached
            
        start=time()
        #if self.hostname != None:
        #    return self.hostname
        
        self.hostname=unknow
        
        
        ######## new method #########
        import socket
        try:
            self.hostname = socket.gethostbyaddr(ip)[0]
            self.add_to_cache( ip, 1 , self.hostname )
            return self.hostname
        except:
            pass
        
        #read hostname from /etc/hosts
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
            
            #print_debug ( "xline=%s" %(xline) )
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
            stdout = self.main.common.exe_cmd(cmd, verbose=0, background=False, lines=1)
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

    def GetUsernameAndHost(self,ip):
        if self.main.xmlrpc.IsStandalone(ip=ip):
            return "%s:%s" %(self.GetUsername(ip), ip)
        else:
            return "%s" %(self.GetUsername(ip) )

    def GetLast(self, ip, ingroup=None):
        last=None
        data={}
        if ip != "" and not self.ipValid(ip):
            ip=self.GetIpAddress(ip)
        hostname=self.GetHostname(ip)
        print_debug("GetLast() ip=%s hostname=%s "%(ip, hostname) )
        
        for i in range(10):
            last_file=WTMP_FILE
            if i != 0:
                last_file=WTMP_FILE+".%d" %i
            if os.path.isfile(last_file):
                print_debug("GetLast() Searching in %s" %last_file)
                a = utmp.UtmpRecord(last_file)
                while 1:
                    b = a.getutent()
                    if not b:
                        break
                    if b[0] == USER_PROCESS:
                        #print_debug("  => Searching for host \"%s:0\" found host=%s ut_line=%s"%(ip, b.ut_host,b.ut_line))
                        if b.ut_host == "%s:0"%(ip) or b.ut_line == "%s:0"%(ip) or b.ut_host == "%s"%hostname :
                            last=b
                a.endutent()
                if last and os.path.isdir("/proc/%s"%last.ut_pid): break
        
        if last and os.path.isdir("/proc/%s"%last.ut_pid):
            # take diff between now and login time
            diff=time()-last.ut_tv[0]
            
            # get days and set diff to rest
            days=int(diff/(3600*24))
            diff=diff-days*3600*24

            # get hours and set diff to rest
            hours=int(diff/3600)
            diff=diff-hours*3600

            # get minutes and set seconds to rest
            minutes=int(diff/60)
            seconds=int(diff-minutes*60)

            print_debug ("GetLast() days=%s hours=%s minutes=%s seconds=%s"%(days, hours, minutes, diff))

            # only print days if > 0    
            if days == 0:
                timelogged="%02dh:%02dm"%(hours,minutes)
            else:
                timelogged="%dd %02dh:%02dm"%(days,hours,minutes)
                
            exclude="noexclude"
            if ingroup != None:
                try:
                    usersingroup=grp.getgrnam(ingroup)[3]
                except Exception, err:
                    usersingroup=[]
                
                for user in usersingroup:
                    if last.ut_user == user:
                        exclude="exclude"
            
            data={"pid":last.ut_pid, "user":last.ut_user, "host":last.ut_host.split(":")[0], "time":last.ut_tv[0], "timelogged":timelogged, "exclude":exclude}
            print_debug("IsLast() data=%s"%data)
        return data
    
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
        
        if self.main.xmlrpc.IsStandalone(ip=ip):
            print_debug("GetUsername(%s) standalone" %ip)
            self.username=self.main.xmlrpc.GetStandalone("get_user")
            return self.username
        
        print_debug("GetUsername(%s) NO standalone" %ip)
        
        if not self.IsActive(ip):
            print_debug ( "GetUsername(%s) not active, returning NO_LOGIN_MSG" %(ip) )
            return shared.NO_LOGIN_MSG
        
        output=self.GetLast(ip)
        if output and output['user']:
            self.username=output['user']
            self.add_to_cache( ip, 2 , self.username )
            return self.username
        """
        cmd="LC_ALL=C LC_MESSAGES=C last| grep -e \"%s:0.*still\" -e \"%s:0.*still\" 2>/dev/null | head -1| awk '{print $1}'" %(ip, self.GetHostname(ip))
        output=self.main.common.exe_cmd(cmd)
        if output != []:
            self.username=output
            self.add_to_cache( ip, 2 , self.username )
            return self.username
        """
        print_debug ( "GetUsername() fail to search username, return unknow" )
        self.add_to_cache( ip, 2 , self.username )
        return self.username
        
    def IsActive(self, host):
        """
        return True or False if host is active
        use xmlrpc echo
        """
        #print_debug ( "IsActive(%s) = %s " %(host, self.main.xmlrpc.GetVersion()) )
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
        self.main.xmlrpc.newhost(host)
        if self.username != None and self.username != shared.NO_LOGIN_MSG and self.username != "---":
            return True
        elif self.GetUsername(host) != shared.NO_LOGIN_MSG:
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
    
    def IsBlockedNet(self, host):
        
        self.main.xmlrpc.newhost(host)
        if self.username != None and self.username != shared.NO_LOGIN_MSG and self.username != "---":
            username=self.username
        elif self.IsLogged(host):
            username=self.username
        else:
            return False
                    
        if self.main.xmlrpc.IsStandalone(host):
            if self.main.xmlrpc.tnc("status", username) == "disabled":
                return True
            else:
                return False
        
        cmd="/usr/lib/tcos/tnc status %s"%(username)
        output=self.main.common.exe_cmd(cmd)
        
        if output == "disabled":
            return True
        elif output == "enabled":
            return False
        elif output == "denied":
            print_debug("You don't have permission to execute tcos-net controller /usr/lib/tcos/tnc")
            return False
        return False
    
    def BlockNet(self, action, username, ports=None, iface=None):
        print_debug("BlockNet() action=%s username=%s ports=%s iface=%s"%(action, username, ports, iface))
        if ports == None: ports=""
        if iface == None: iface=""
        cmd="/usr/lib/tcos/tnc %s %s %s %s"%(action, ports, iface, username)
        output=self.main.common.exe_cmd(cmd)
        print_debug("output=%s"%output)
        return output
        
    def isExclude(self, host, ingroup=None):
        if self.username == shared.NO_LOGIN_MSG:
            return False

        output=self.GetLast(host, ingroup)
        if output and output['exclude'] == "exclude":
            return True
        return False

    def GetUserID(self, username):
        try:
            uid=pwd.getpwnam(username)[2]
        except Exception, err:
            uid=None
            print_debug("GetUserID Exception error %s"%err)
        return uid

    def GetNumProcess(self, host):
        """
        return number of process
        """
        self.main.xmlrpc.newhost(host)
        if self.username != None and self.username != shared.NO_LOGIN_MSG and self.username != "---":
            username=self.username
        elif self.IsLogged(host):
            username=self.username
        else:
            return "---"
        
        #self.username=self.GetUsername(host)
        
        if self.main.xmlrpc.IsStandalone(host):
            return self.main.xmlrpc.GetStandalone("get_process")
        
        # use uid to support long usernames (>8)
        uid=self.GetUserID(self.username)
        cmd="ps U %s -o pid | sed 's/[[:blank:]]//g' | grep -c ^[0-9]"%(uid)
        process=self.main.common.exe_cmd(cmd)
        
        print_debug ("GetNumProcess() process=%s" %(process) )
        return process
    
    
        
    def GetTimeLogged(self, host):
        #if self.username == None:
        #    self.username=self.GetUsername(host)
        #
        if self.username == shared.NO_LOGIN_MSG:
            return "---"

        
        output=self.GetLast(host)
        if output and output['timelogged']:
            return output['timelogged']
        
        # no time
        return "---"
        
if __name__ == '__main__':
    shared.debug=True
    local=LocalData (None)
    import sys
    print local.GetLast(sys.argv[1])
    #local.GetAllClients()
    #local.GetHostname("192.168.0.2")
    #local.GetHostname("192.168.0.10")
    #local.GetUsername("192.168.0.10")
    #local.GetTimeLogged("192.168.0.10")
