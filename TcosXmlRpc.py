# -*- coding: UTF-8 -*-
##########################################################################
# TcosMonitor writen by MarioDebian <mariodebian@gmail.com>
#
#    TcosMonitor version __VERSION__
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

import xmlrpclib
from time import time, sleep
import sys
import os
import re
import popen2
import shared
from gettext import gettext as _
import socket


if "DISPLAY" in os.environ:
    if os.environ["DISPLAY"] != "":
        import gtk


def print_debug(txt):
    if shared.debug:
        print "%s::%s" %(__name__, txt)


def howmany(start, txt):
    print_debug ("howmany() Time to %s=%f" %(txt, (time() - start)) )



class TcosXmlRpc:
    def __init__(self, main):
        print_debug ( "__init__()" )
        self.main=main
        self.ip=None
        self.version=None
        self.logged=False
        self.connected=False
        self.url=None
        self.tc=None
        self.ports=[]
        
        if self.main != None:
            self.cache_timeout=self.main.config.GetVar("cache_timeout")
            self.username=self.main.config.GetVar("xmlrpc_username")
            self.password=self.main.config.GetVar("xmlrpc_password")
            
            print_debug ( "__init__() login=%s pass=%s" %(self.username, self.password) )
            
            if self.username == "" or self.password == "":
                # warn empty username and password 
                if self.main.name == "TcosMonitor":
                    print _("Username or password are empty,\nplease edit in preferences dialog!")
                    gtk.gdk.threads_enter()
                    shared.error_msg( _("Username or password are empty,\nplease edit in preferences dialog!") )
                    gtk.gdk.threads_leave()
        else:
            print_debug ( "running outside tcosmonitor" )

    def isLive(self, ip):
        """
        check if host is accesible by network
        """
        cached=self.cache(ip, "")
        if cached != None:
            return cached
        
        print_debug( "isLive(%s) make ping..." %(ip) )
        pingaling = os.popen("ping -W 1 -q -c1 "+ip,"r")
        lifeline = re.compile(r"(\d) received")
        while 1:
            line = pingaling.readline()
            if not line: break
            igot = re.findall(lifeline,line)
            if igot:
                status = int(igot[0])
                if status == 1:
                    print_debug ( "isLive(%s) True" %(ip) )
                    self.ports.append( [ip, "", True, time()] )
                    return True
                else:
                    print_debug ( "isLive(%s) False" %(ip) )
                    self.ports.append( [ip, "", False, time()] )
                    return False
    
    def cache(self, ip, port):
        """
        self.ports is an array that contains:
            [ip, port, True/False, time()]
        we cache num self.cache_timeout sec petittions
        """
        self.cache_timeout=self.main.config.GetVar("cache_timeout")
        #print_debug ( "cache(%s, %s) cache_timeout=%s" %(ip, port, self.cache_timeout) )
        for i in range(len(self.ports)):
            #print data
            if self.ports[i][0] == ip:
                if port == "" or self.ports[i][1] == port:
                    # we have same ip and same port
                    print_debug ( "cache() %s cached from %s secs ¿<? timeout=%s" \
                            %(self.ports[i][2], float(time() - self.ports[i][3]), self.cache_timeout ) )
                    if float(time() - float(self.ports[i][3]) ) < float(self.cache_timeout):
                        print_debug ( "cache() IS CACHED, returning %s" %(self.ports[i][2]) )
                        return self.ports[i][2]
                    else:
                        print_debug ( "cache() delete old cache" )
                        #print self.ports
                        self.ports.pop(i)
                        print_debug ( self.ports )
                        return None
        return None
                    
    def isPortListening(self, ip, port):
        """
        check if ip and port is live and running something (using sockets)
        
        """
        cached=None
        
        print_debug ( "isPortListening(%s:%s) __init__" %(ip,port) )
        if self.main != None:
            cached=self.cache(ip, port)
            
        if cached != None:
            return cached
            
        if ip == None:
            return True
        if port == None:
            return True
        #if not self.isLive(ip):
        #    return False
        
        from ping import PingPort
        status=PingPort(ip,port).get_status()
        print_debug ( "isPortListening() status=%s" %(status) )
        if status == "OPEN":
            return True
        else:
            return False
        """
        cmd="echoping -h / %s:%s 2>&1" %(ip, port)
        print_debug ( "isPortListening() cmd=%s" %(cmd) )
        listen=os.popen(cmd, "r")
        for line in listen.readlines():
            #print line
            if "404" in line:
                print_debug ( "isPortListening() 404 found" )
                self.ports.append( [ip, port, True, time()] )
                return True
                
            if "Elapsed" in line:
                print_debug ( "isPortListening() Elapsed found" )
                self.ports.append( [ip, port, True, time()] )
                return True
                
            if "refused" in line:
                print_debug ( "isPortListening() Connection refused" )
                self.ports.append( [ip, port, False, time()] )
                return False
            
        # if unknow return False but don't cache
        return False
        """
                
    def newhost(self, ip):
        print_debug ( "newhost(%s)" %(ip) )
        self.ip=ip
        self.version=None
        self.logged=None
        cached = None
        
        if self.main == None:
            print_debug ( "newhost() seems to run outside tcosmonitor" )
        else:
            cached=self.cache(ip, shared.xmlremote_port)
        
        print_debug ( "cached=%s" %(cached) )
        
        if cached == None:
            if not self.isPortListening(ip, shared.xmlremote_port):
                self.connected=False
                return
                    
        self.url = 'http://%s:%d/RPC2' %(self.ip, shared.xmlremote_port)
        try:
            # set min socket timeout
            socket.setdefaulttimeout(2)
            self.tc = xmlrpclib.Server(self.url)
            #echo=self.tc.tcos.echo("test")
            self.connected=True
            # save socket default timeout
            socket.setdefaulttimeout(shared.socket_default_timeout)
            print_debug ( "newhost() tcosxmlrpc running on %s" %(self.ip) )
        except:
            print_debug("newhost() ERROR conection unavalaible !!!")
            self.connected=False
        
    def login(self):
        print_debug ( "\n\nDELETE ME\n\n" )
        return
        """
        if not self.isPortListening(self.ip, shared.xmlremote_port):
            self.connected=False
            return
        self.username=self.main.config.GetVar("xmlrpc_username")
        self.password=self.main.config.GetVar("xmlrpc_password")
        if self.url == None:
            print_debug ("login() no host!!!"  )
            shared.error_msg( _("No host specified") )
            return False
        
        print_debug ("login() url=%s user=%s pass=******" \
                                %(self.url, self.username) )
        try:
            auth=self.tc.tcos.login(self.username, self.password)
        except:
            auth="ko"
            print_debug("login() ERROR conection unavalaible !!!")
            self.main.write_into_statusbar( _("Can't login, connection unavalaible") )
        if auth == "ok":
            self.logged=True
            return True
        else:
            self.logged=False
            return False
        """
    def logout(self):
        print_debug ( "\n\nDELETE ME\n\n" )
        return
        """
        if self.logged:
            self.tc.tcos.logout()
            self.logged=False
        """
    def GetVersion(self):
        if not self.connected:
            print_debug ("GetVersion() Error, NO CONNECTION!!")
            return None
        if self.version != None:
            return self.version
        try:
            self.version=self.tc.tcos.version()
            #print_debug("tcos version \"%s\"" %(self.version) )
            #mayor, med, minor = self.version.split('.')
            #if int(minor) < 10:
            #    shared.info_msg ( "Please update tcosxmlrpc terminal version, need 0.0.11, have %s" %(self.version) )
            return self.version
        except:
            return None
    
        
    def Exe(self, cmd):
        """
        Exe a command in thin client
        """
        print_debug ("EXE() INIT, %s" %(cmd) )
        if not self.connected:
            print_debug ("Exe() Error, NO CONNECTION!!")
            return None
        
        print_debug ("Exe(): user=\"%s\" pass=\"%s\" " \
           %(self.main.config.GetVar("xmlrpc_username"), self.main.config.GetVar("xmlrpc_password")) )
        
        #self.login ()
        #if not self.logged:
        #    print_debug ("Exe() Error, NO LOGGED!!")
        #    return None
        self.tc.tcos.exe(cmd,\
         self.main.config.GetVar("xmlrpc_username"),\
          self.main.config.GetVar("xmlrpc_password"))
        
    def Kill(self, app):
        """
        kill a running app in thin client
        """
        print_debug ("Kill() INIT, %s" %(app) )
        if not self.connected:
            print_debug ("Kill() Error, NO CONNECTION!!")
            return None
        
        #self.login ()
        #if not self.logged:
        #    print_debug ("Kill() Error, NO LOGGED!!")
        #    return None
        self.tc.tcos.kill(app,\
         self.main.config.GetVar("xmlrpc_username"), \
         self.main.config.GetVar("xmlrpc_password"))
    
    def GetStatus(self, cmd):
        """
        get cmd and exec a xmlrpc request
        parse value, and return:
            1 if running
            0 if not running
            None if access denied
        """
        if not self.connected:
            print_debug ("GetStatus() Error, NO CONNECTION!!")
            return None
        
        #if not self.logged:
        #    print_debug ("GetStatus() Error, NOT LOGGED!!")
        #    return None
        
        status=self._ParseResult( self.tc.tcos.status(cmd) )
        if status == "1":
            print_debug ("GetStatus() %s is running" %(cmd) )
            return True
        else:
            print_debug ("GetStatus() %s is NOT running" %(cmd) )
            return False
    
    def _ParseResult(self, txt):
        print_debug ( "_ParseResult(%s)" %(txt) )
        if txt == None or txt == True or txt == False:
            return txt
            
        if txt.find("error") == 0:
            #shared.info_msg ( "Error from tcosxmlrpc:\n\n%s" %(txt) )
            return None
        else:
            return txt

    def ReadInfo(self, string):
        """
        server.tcos.info("cpu_model").replace('\n', '')
        """
        if not self.connected:
            print_debug ( "ReadInfo() NO CONNECTION" )
            return None
        result=self.tc.tcos.info(string).replace('\n', '')
        if result.find('error') == 0:
            print_debug ( "ReadInfo(%s): ERROR, result contains error string!!!" %string )
            #self.main.write_into_statusbar( "ERROR: %s" %(result) )
            return ""
        else:
            return result

    def IsStandalone(self, ip=None):
        if not ip:
            print_debug("IsStandalone() WARNING using old IP: %s" %self.ip)
        else:
            self.newhost(ip)
        
        if not self.connected:
            print_debug("IsStandalone() NO CONNECTION")
            return False
        
        print_debug("IsStandalone() ip=%s" %self.ip)
        
        if self.ReadInfo("get_client") == "standalone":
            return True
        return False
    

    def GetStandalone(self, item):
        if item == "get_user":
            if not self.connected:
                print_debug ( "GetStandalone() NO CONNECTION" )
                return shared.NO_LOGIN_MSG
            result=self.tc.tcos.standalone("get_user").replace('\n', '')
            if result.find('error') == 0:
                print_debug ( "GetStandalone(\"get_user\"): ERROR, result contains error string %s!!!" %result )
                return shared.NO_LOGIN_MSG
            elif result == "":
                print_debug("GetStandalone() no user connected")
                return shared.NO_LOGIN_MSG
            else:
                return result
                
        elif item == "get_process":
            return self.tc.tcos.standalone("get_process").replace('\n', '')
            
        else:
            return ""
    
    
    def DBus(self, admin, passwd, action, data):
        username=self.GetStandalone("get_user")
        remote_user=self.main.config.GetVar("xmlrpc_username")
        remote_passwd=self.main.config.GetVar("xmlrpc_password")
        cmd="--auth='%s:%s' --type=%s --text='%s' --username=%s" %(admin, passwd, action, data, username )
        print_debug ("DBus() cmd=%s" %(cmd) )
        return self.tc.tcos.dbus(cmd, remote_user, remote_passwd).replace('\n', '')
        
    def GetSoundChannels(self):
        """
        Exec soundctl.sh with some of these args
            --showcontrols          ( return all mixer channels )
            --getlevel CHANNEL      ( return CHANNEL level xx% xx% left and right )
            --setlevel CHANNEL xx%  ( change and return CHANNEL level xx% xx% left and right )
            --getmute CHANNEL       ( return off if mute or on if unmute CHANNEL )
            --setmute CHANNEL       ( mute CHANNEL and return off if succesfull )
            --setunmute CHANNEL     ( unmute CHANNEL and return on if succesfull )
        """
        
        if self.main.name == "TcosVolumeManager":
            user=self.main.xauth.get_cookie()
            passwd=self.main.xauth.get_hostname()
            if user == None:
                print_debug ( "GetSoundChannels() error loading cookie info" )
                return None
        else:
            user=self.main.config.GetVar("xmlrpc_username")
            passwd=self.main.config.GetVar("xmlrpc_password")

        print_debug ( "GetSoundChannels() user=%s passwd=%s" %(user, passwd) )

        if not self.connected:
            print_debug ( "GetSoundChannels() NO CONNECTION" )
            return None
            
        result=self.tc.tcos.sound("--showcontrols", "", user, passwd ).replace('\n', '')

        if result.find('error') == 0:
            print_debug ( "GetSoundChannels(): ERROR, result contains error string!!!\n%s" %(result))
            #self.main.write_into_statusbar( "ERROR: %s" %(result) )
            return ""
        else:
            number=len(result.split('|'))
            return result.split('|')[:number-1]

    def GetSoundInfo(self, channel, mode="--getlevel"):
        """
        mode = "--getlevel"
        mode = "--getmute"
        mode = "--getserverinfo"
        """
        #print_debug ( "GetSoundInfo(\"%s\", \"%s\")" %(channel, mode) )
        #if channel == "":
        #    return None
        user=self.main.config.GetVar("xmlrpc_username")
        passwd=self.main.config.GetVar("xmlrpc_password")
        if self.main.name == "TcosVolumeManager":
            user=self.main.xauth.get_cookie()
            passwd=self.main.xauth.get_hostname()

        if not self.connected:
            print_debug ( "GetSoundInfo() NO CONNECTION" )
            return None

        result=self.tc.tcos.sound(mode, " \"%s\" " %(channel), user, passwd ).replace('\n', '')

        if result.find('error') == 0:
            print_debug ( "GetSoundInfo(): ERROR, result contains error string!!!\n%s" %(result))
            #self.main.write_into_statusbar( "ERROR: %s" %(result) )
            return ""
        else:
            return result

    def SetSound(self, ip, channel, value, mode="--setlevel"):
        if channel == "":
            return None
        if not self.connected:
            print_debug ( "GetSoundInfo() NO CONNECTION" )
            return None
        user=self.main.config.GetVar("xmlrpc_username")
        passwd=self.main.config.GetVar("xmlrpc_password")
        if self.main.name == "TcosVolumeManager":
            user=self.main.xauth.get_cookie()
            passwd=self.main.xauth.get_hostname()

        result=self.tc.tcos.sound(mode, " \"%s\" \"%s\" " %(channel,value), user, passwd).replace('\n', '')

        if result.find('error') == 0:
            print_debug ( "GetSoundInfo(): ERROR, result contains error string!!!\n%s" %(result))
            #self.main.write_into_statusbar( "ERROR: %s" %(result) )
            return ""
        else:
            return result

    def GetDevicesInfo(self, device, mode="--getsize"):
        if not self.connected:
            print_debug ( "GetDevicesInfo() NO CONNECTION" )
            return None
        remote_hostname=self.main.xauth.get_hostname()
        xauth_cookie=self.main.xauth.get_cookie()
        if mode == "--getxdrivers":
            xauth_cookie="foo"
        if xauth_cookie == None:
            return "GetDevicesInfo error: xauth cookie don't match"
        # don't fail if timeout
        try:
            result=self.tc.tcos.devices(mode, " \"%s\" " %(device), \
                                       xauth_cookie, \
                                       remote_hostname ).replace('\n', '')
            if "error" in result:
                print_debug ( "GetDevicesInfo(): ERROR, result contains error string!!!\n%s" %(result))
                return result
            else:
                return result
        except:
            return ""

    def lockscreen(self):
        if self.isPortListening(self.ip, shared.xmlremote_port):
            #self.login ()
            self.tc.tcos.exe("lockscreen", \
             self.main.config.GetVar("xmlrpc_username"), \
             self.main.config.GetVar("xmlrpc_password"))
             
            return True
        return False
        
    def unlockscreen(self):
        if self.isPortListening(self.ip, shared.xmlremote_port):
            #self.login ()
            self.tc.tcos.kill("lockscreen",\
             self.main.config.GetVar("xmlrpc_username"), \
             self.main.config.GetVar("xmlrpc_password"))
             
            return True
        return False

    def status_lockscreen(self):
        if self.isPortListening(self.ip, shared.xmlremote_port):
            #self.login ()
            result=self._ParseResult(self.GetStatus("lockscreen"))
            print_debug ( "lockscreen() %s" %(result) )
            return result
        return False
    
    
        
    def screenshot(self, size="65"):
        print_debug ( "screenshot() %s" %(size) )
        try:
            result=self._ParseResult( self.tc.tcos.screenshot(\
                     "%s" %(size),\
                     self.main.config.GetVar("xmlrpc_username"), \
                     self.main.config.GetVar("xmlrpc_password")) )
                     
            print_debug ( "screenshot(size=%s percent) %s" %(size, result) )
            return True
        except:
            # connection error
            return False
        
        

        
if __name__ == '__main__':
    app=TcosXmlRpc (None)
    
    #app.newhost("192.168.0.10")
    #app.newhost("localhost")
    #app.isLive("192.168.0.10")
    #app.isLive("192.168.0.3")
    """
    app.isLive("192.168.0.1")
    
    if app.isPortListening("192.168.0.3", "80"):
        print "80 is listening"
    else:
        print "80 is NOT listening"
        
    if app.isPortListening("192.168.0.3", "8080"):
        print "8080 is listening"
    else:
        print "8080 is NOT listening"
    """
    app.isLive("192.168.0.11")
    
    """
    if app.isPortListening("192.168.0.10", "8080"):
        print "8080 is listening"
    else:
        print "8080 is NOT listening"
    
    app.isLive("192.168.0.10")
    
    if app.isPortListening("192.168.0.10", "8080"):
        print "8080 is listening"
    else:
        print "8080 is NOT listening"
    """
    if app.isPortListening("192.168.0.11", "8080"):
        print "8080 is listening"
    else:
        print "8080 is NOT listening"
    
    app.isLive("192.168.0.11")
    print "waiting"
    sleep(6)
    app.isLive("192.168.0.11")
    
    #if app.isPortListening("192.168.0.10", "8080"):
    #    print "8080 is listening"
    #else:
    #    print "8080 is NOT listening"
    #start=time()
    #print_debug ("TCOS_VERSION:  %s" %(app.GetVersion()) ) 
    #howmany(start, "get version info")
    
    #start=time()
    #print_debug ("TCOS_«tilda»_STATUS:  %s" %(app.GetStatus("tilda2")) )
    #howmany(start, "get status of tilda")
    
    #app.Exe("xterm")
    #app.status_lockscreen()
    #app.lockscreen()
    #sleep(2)
    #app.status_lockscreen()
    #app.unlockscreen()
    #app.Exe("glxgears -printfps > glxgears.log")

    #start=time()
    #app.logout()
    #howmany(start, "logout")
