# -*- coding: UTF-8 -*-
##########################################################################
# TcosMonitor writen by MarioDebian <mariodebian@gmail.com>
#
# TcosMonitor version __VERSION__
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


from subprocess import Popen, PIPE, STDOUT
import os
import sys
import socket


import shared
def print_debug(txt):
    if shared.debug:
        print "%s::%s" %("TcosXauth", txt)
    return
        

class TcosXauth:
    def __init__(self, main):
        self.main=main
        self.cookie=None
        self.get_display()

    def get_display(self):
        self.display_host=os.environ["DISPLAY"].split(':')[0]
        self.display_hostname=self.display_host
        self.display_ip=self.display_host

        # read hostname and ipaddress based on cookie hostname/ip
        try:
            if self.display_host != "":
                self.display_hostname=socket.gethostbyaddr(self.display_host)[0]
                self.display_ip=socket.gethostbyaddr(self.display_host)[2][0]
        except:
            pass

        print_debug ( "get_display() display_host=%s display_hostname=%s display_ip=%s" %(self.display_host, self.display_hostname, self.display_ip) )

    def init_standalone(self):
        print_debug ( "init_standalone() " )
        self.get_display()
        self.name="TcosXauth"
        import TcosConf
        import TcosXmlRpc
        self.config=TcosConf.TcosConf(self, openfile=False)
        self.xmlrpc=TcosXmlRpc.TcosXmlRpc(self)

    def read_cookie(self):
        if self.cookie != None:
            # return last cookie (cookie in X session don't change)
            return self.cookie
        
        print_debug ( "read_cookie() exec \"xauth list\"" )
        p = Popen("xauth -n list", shell=True, bufsize=0, stdout=PIPE, stderr=STDOUT)
        readed=p.stdout.read()
        readed=readed.split('\n')[0:-1]
        print_debug ( "read_cookie() %s" %readed )
        for line in readed:
            if len(line.split()) != 3:
                continue
            host, ctype, cookie = line.split()
            chost=host.split(':')[0]
            if chost == self.display_host or chost == self.display_hostname or chost == self.display_ip:
                self.cookie=cookie
                print_debug ( "read_cookie() chost=%s HAVE COOKIE => %s" %(chost, cookie) )
                return cookie
        return None
        
    def get_cookie(self):
        return self.read_cookie()
        
    def get_hostname(self):
        return self.display_hostname

    def set_hostname(self, hostname):
        self.display_host=hostname
        self.display_hostname=hostname

    def test_auth(self):
        cookie=self.read_cookie()
        if cookie == None:
            print_debug ( "test_auth() Can't read cookie" )
            return
        self.xmlrpc.newhost(self.display_hostname)
        if not self.xmlrpc.connected:
            print_debug ( "test_auth() No connection" )
            return
        returned = self.xmlrpc.tc.tcos.xauth(cookie, self.display_hostname)
        if "OK" in returned: return True
        elif "error" in returned: return False



if __name__ == "__main__":
    shared.debug=True
    app=TcosXauth(None)
    app.init_standalone()
    app.set_hostname("tcos27")
    if app.test_auth():
        print "Xauth OK"
    else:
        print "Xauth error"
