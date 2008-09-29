# -*- coding: UTF-8 -*-
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


from subprocess import Popen, PIPE, STDOUT
#import os
#import sys
#import socket


import shared
def print_debug(txt):
    if shared.debug:
        print "%s::%s" % ("TcosXauth", txt)
    return


import TcosCommon
import TcosConf
import TcosXmlRpc

class TcosXauth:
    def __init__(self, main):
        self.main=main
        self.cookie=None
        
        self.common=TcosCommon.TcosCommon(self)
        self.display_host=self.common.get_display(ip_mode=False)
        self.display_ip=self.common.get_display(ip_mode=True)

    def init_standalone(self):
        print_debug ( "init_standalone() " )
        self.name="TcosXauth"
        self.config=TcosConf.TcosConf(self, openfile=False)
        self.xmlrpc=TcosXmlRpc.TcosXmlRpc(self)
        
    def read_cookie(self):
        if self.cookie != None:
            # return last cookie (cookie in X session don't change)
            return self.cookie
        
        print_debug ( "read_cookie() exec \"xauth list\"" )
        p = Popen(["xauth", "-n", "list"], shell=False, bufsize=0, stdout=PIPE, stderr=STDOUT, close_fds=True)
        readed=p.stdout.read()
        readed=readed.split('\n')[0:-1]
        print_debug ( "read_cookie() %s" %readed )
        for line in readed:
            if len(line.split()) != 3:
                continue
            host, ctype, cookie = line.split()
            chost=host.split(':')[0]
            if chost == self.display_host or chost == self.display_ip:
                self.cookie=cookie
                print_debug ( "read_cookie() chost=%s HAVE COOKIE => %s" %(chost, cookie) )
                return cookie
        return None
        
    def get_cookie(self):
        return self.read_cookie()
        
    def get_hostname(self):
        return self.display_ip

    def test_auth(self):
        cookie=self.read_cookie()
        print_debug("test_auth() cookie=%s ip=%s"%(cookie, self.display_ip))
        if cookie == None:
            print_debug ( "test_auth() Can't read cookie" )
            return
        self.xmlrpc.newhost(self.display_ip)
        if not self.xmlrpc.connected:
            print_debug ( "test_auth() No connection" )
            return
        try:
            returned = self.xmlrpc.tc.tcos.xauth(cookie, self.display_ip)
        except Exception, err:
            print_debug("test_auth() Exception error: %s"%err)
            returned = "error"
        
        if "OK" in returned: return True
        else: return False



if __name__ == "__main__":
    shared.debug=True
    app=TcosXauth(None)
    app.init_standalone()
    if app.test_auth():
        print "Xauth OK"
    else:
        print "Xauth error"
