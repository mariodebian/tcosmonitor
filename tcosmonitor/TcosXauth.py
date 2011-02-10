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


import sys
import binascii
from Xlib import xauth

from tcosmonitor import shared
def print_debug(txt):
    if shared.debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)


import tcosmonitor.TcosCommon
import tcosmonitor.TcosConf
import tcosmonitor.TcosXmlRpc

class TcosXauth(object):
    def __init__(self, main):
        self.main=main
        self.cookie=None
        
        self.common=tcosmonitor.TcosCommon.TcosCommon(self)
        self.display_host=self.common.get_display(ip_mode=False)
        self.display_ip=self.common.get_display(ip_mode=True)
        
        print_debug("display_host='%s'" %self.display_host)
        print_debug("display_ip='%s'" %self.display_ip)

    def init_standalone(self):
        print_debug ( "init_standalone() " )
        self.name="TcosXauth"
        self.config=tcosmonitor.TcosConf.TcosConf(self, openfile=False)
        self.xmlrpc=tcosmonitor.TcosXmlRpc.TcosXmlRpc(self)
        
    def read_cookie(self):
        if self.cookie != None:
            # return last cookie (cookie in X session don't change)
            return self.cookie
        
        # use python-xlib for getting IPAddress and data (support IPV6)
        for line in self.parseDisplay():
            if line[0] == self.display_host or line[0] == self.display_ip:
                self.cookie=line[1]
                return self.cookie
        
        return None

    def parseDisplay(self):
        """
        read xauth and get IP addr using xlib python bindings
        """
        a=xauth.Xauthority()
        entries=a.entries
        lines=[]
        for entry in entries:
            ipv4=str(shared.parseIPAddress(entry[1], return_ipv4=True))
            if ipv4 is None:
                ipv4=entry[1]
            cookie=self.parseCookie(entry[4])
            print_debug("parseDisplay() ip=%s cookie=%s"%(ipv4, cookie))
            lines.append([ipv4, cookie])
        return lines

    def parseCookie(self, cookiestr):
        """
        read bin cookie and return hex string
        """
        cookie=[]
        for i in cookiestr:
            cookie.append(binascii.hexlify(i))
        return "".join(cookie)

    def get_cookie(self):
        return self.read_cookie()
        
    def get_hostname(self):
        return self.display_ip

    def test_auth(self, nossl=False):
        cookie=self.read_cookie()
        print_debug("test_auth() cookie=%s ip=%s"%(cookie, self.display_ip))
        if cookie == None:
            print_debug ( "test_auth() Can't read cookie" )
            return
        self.xmlrpc.newhost(self.display_ip, nossl)
        if not self.xmlrpc.connected:
            print_debug ( "test_auth() No connection" )
            return
        try:
            returned = self.xmlrpc.tc.tcos.xauth(cookie, self.display_ip)
        except Exception, err:
            print_debug("test_auth() Exception error: %s"%err)
            returned = "error"
        
        if "OK" in returned:
            return True
        else: return False



if __name__ == "__main__":
    shared.debug=True
    app=TcosXauth(None)
    app.init_standalone()
    if app.test_auth():
        print "Xauth OK"
    else:
        print "Xauth error"
