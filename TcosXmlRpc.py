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

import xmlrpclib
from time import time, sleep
import sys
import os
import re
import shared
from gettext import gettext as _
import socket
from subprocess import Popen, PIPE, STDOUT


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
        self.lock=False
        self.ports=[]
        self.resethosts()
        
        if self.main != None:
            self.cache_timeout=self.main.config.GetVar("cache_timeout")
            self.username=self.main.config.GetVar("xmlrpc_username")
            self.password=self.main.config.GetVar("xmlrpc_password")
            
            if self.username == "" or self.password == "":
                # warn empty username and password 
                if self.main.name == "TcosMonitor":
                    #gtk.gdk.threads_enter()
                    self.main.common.threads_enter("TcosXmlRpc:__init__ no user or password")
                    shared.error_msg( _("Username or password are empty,\nplease edit in preferences dialog!") )
                    #gtk.gdk.threads_leave()
                    self.main.common.threads_leave("TcosXmlRpc:__init__ no user or password")
        else:
            print_debug ( "running outside tcosmonitor" )

    def resethosts(self):
        self.lasthost=None
        self.lastport=None
        self.laststandalone_ip=None
        self.aliveStatus=None
        self.isStandAlone=None

    def wait(self):
        """
        wait (max 4 sec) for self.lock == True
        """
        print_debug("##############  wait() lock=%s  #################"%self.lock)
        if not self.lock: return
        i=0
        for i in range(40):
            print_debug("##############  wait() i=%s  ##############"%i)
            if not self.lock: return
            sleep(0.1)

    def isLive(self, ip):
        """
        check if host is accesible by network
        """
        cached=self.cache(ip, "")
        if cached != None:
            return cached
        
        print_debug( "isLive(%s) make ping..." %(ip) )
        pingalingout = Popen(["ping", "-q", "-W1", "-c1", "%s" %ip], shell=False, stdout=PIPE, stderr=STDOUT, close_fds=True)
        pingalingout.wait()
        pingaling = pingalingout.stdout
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
    

    def isPortListening(self, ip, port):
        """
        check if ip and port is live and running something (using sockets)
        
        """
        if not ip:   return False
        if not port: return False
        
        # this avoid to scan same ip a lot of times, but can give errors FIXME
        if self.lasthost == ip and self.aliveStatus == "OPEN":
            print_debug("isPortListening() not scanning again, using lastip=%s OPEN" %(ip))
            return True
        elif self.lasthost == ip and self.aliveStatus == "CLOSED":
            print_debug("isPortListening() not scanning again, using lastip=%s CLOSED" %(ip))
            return False
        
        from ping import PingPort
        self.aliveStatus=PingPort(ip,port).get_status()
        self.lastport=port
        #print_debug ( "isPortListening() PING PORT DONE status=%s" %(self.aliveStatus) )
        if self.aliveStatus == "OPEN":
            print_debug ( "isPortListening(%s:%s) PinPort => OPEN" %(ip,port))
            return True
        else:
            print_debug ( "isPortListening(%s:%s) PinPort => CLOSED" %(ip,port) )
            return False
        
                
    def newhost(self, ip):
        #print_debug ( "newhost(%s)" %(ip) )
        self.ip=ip
        self.version=None
        self.logged=None
        cached = None
        
        # this avoid to scan same ip a lot of times, but can give errors FIXME
        if self.lasthost == ip and self.connected:
            print_debug("newhost() not scanning again, using lastip=%s" %(ip))
            return
        
        # change ip, force new
        if self.lasthost != ip:
            self.resethosts()
        
        self.lasthost=ip 
        
        if not self.isPortListening(ip, shared.xmlremote_port):
            self.connected=False
            return
        
        self.url = 'http://%s:%d/RPC2' %(self.ip, shared.xmlremote_port)
        try:
            # set min socket timeout to 2 secs
            socket.setdefaulttimeout(2)
            self.tc = xmlrpclib.Server(self.url)
            self.connected=True
            # save socket default timeout
            socket.setdefaulttimeout(shared.socket_default_timeout)
            print_debug ( "newhost() tcosxmlrpc running on %s" %(self.ip) )
        except Exception, err:
            print_debug("newhost() ERROR conection unavalaible !!! error: %s"%err)
            self.connected=False
        

    def GetVersion(self):
        if not self.connected:
            print_debug ("GetVersion() Error, NO CONNECTION!!")
            return None
        if self.version != None:
            return self.version
        try:
            self.version=self.tc.tcos.version()
            return self.version
        except Exception, err:
            print_debug("GetVersion() Exception error %s"%err)
            return None
    
        
    def Exe(self, cmd):
        """
        Exe a command in thin client
        """
        print_debug ("EXE() INIT, %s" %(cmd) )
        if not self.connected:
            print_debug ("Exe() Error, NO CONNECTION!!")
            return None
        
        print_debug ("Exe(): user=\"%s\" pass=\"******\" " \
           %(self.main.config.GetVar("xmlrpc_username") ) )
        
        try:
            self.tc.tcos.exe(cmd,\
              self.main.config.GetVar("xmlrpc_username"),\
              self.main.config.GetVar("xmlrpc_password"))
        except Exception, err:
            print_debug("Exe() Exception error %s"%err)
            pass
        
    def Kill(self, app):
        """
        kill a running app in thin client
        """
        print_debug ("Kill() INIT, %s" %(app) )
        if not self.connected:
            print_debug ("Kill() Error, NO CONNECTION!!")
            return None
        
        try:
            self.tc.tcos.kill(app,\
              self.main.config.GetVar("xmlrpc_username"), \
              self.main.config.GetVar("xmlrpc_password"))
        except Exception, err:
            print_debug("Kill() Exception error %s"%err)
            pass
    
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
        
        try:
            status=self._ParseResult( self.tc.tcos.status(cmd) )
        except Exception, err:
            print_debug("GetStatus() Exception PARSER error %s"%err)
            return False

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
        try:
            result=self.tc.tcos.info(string).replace('\n', '')
        except Exception, err:
            print_debug ( "ReadInfo(%s): ERROR, can't connect to XMLRPC server!!! error %s" %(string,err) )
            return ""
        if result.find('error') == 0:
            print_debug ( "ReadInfo(%s): ERROR, result contains error string!!!" %string )
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
        
        # use last data
        if self.laststandalone_ip == ip:
            return self.isStandAlone
        
        self.laststandalone_ip=ip
        
        if self.ReadInfo("get_client") == "standalone":
            print_debug("IsStandalone() ip=%s TRUE" %ip)
            self.isStandAlone=True
            return True
        
        print_debug("IsStandalone() ip=%s FALSE" %ip)
        self.isStandAlone=False    
        return False
    

    def GetStandalone(self, item):
        if item == "get_user":
            if not self.connected:
                print_debug ( "GetStandalone() NO CONNECTION" )
                return shared.NO_LOGIN_MSG
            try:
                result=self.tc.tcos.standalone("get_user").replace('\n', '')
            except Exception, err:
                print_debug("GetStandalone(get_user) Exception error: %s"%err)
                return shared.NO_LOGIN_MSG
            
            if result.find('error') == 0:
                return shared.NO_LOGIN_MSG
            elif result == "":
                return shared.NO_LOGIN_MSG
            else:
                return result
                
        elif item == "get_process":
            try:
                return self.tc.tcos.standalone("get_process").replace('\n', '')
            except Exception, err:
                print_debug("GetStandalone(get_process) Exception error: %s"%err)
                return ""
        
        elif item == "get_server":
            try:
                return self.tc.tcos.standalone("get_server").replace('\n', '')
            except Exception, err:
                print_debug("GetStandalone(get_server) Exception error %s"%err)
                return ""
        
        elif item == "get_time":
            try:
                return self.tc.tcos.standalone("get_time").replace('\n', '')
            except Exception, err:
                print_debug("GetStandalone(get_time) Exception error %s"%err)
                return None
            
        else:
            return ""
    
    
    def DBus(self, action, data):
        username=self.GetStandalone("get_user")
        remote_user=self.main.config.GetVar("xmlrpc_username")
        remote_passwd=self.main.config.GetVar("xmlrpc_password")
        cmd="--auth='%s:%s' --type=%s --text='%s' --username=%s" %(remote_user, remote_passwd, action, data, username )
        print_debug ("DBus() cmd=%s" %(cmd) )
        try:
            return self.tc.tcos.dbus(cmd, remote_user, remote_passwd).replace('\n', '')
        except Exception, err:
            print_debug("DBus Exception error %s"%err)
            return None
        
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
            print_debug ( "GetSoundChannels() cookie=%s hostname=%s" %(user, passwd) )
        else:
            user=self.main.config.GetVar("xmlrpc_username")
            passwd=self.main.config.GetVar("xmlrpc_password")

        

        if not self.connected:
            print_debug ( "GetSoundChannels() NO CONNECTION" )
            return None
            
        try:
            result=self.tc.tcos.sound("--showcontrols", "", user, passwd ).replace('\n', '')
        except Exception, err:
            print_debug("GetSoundChannels(--showcontrols) Exception error: %s"%err)
            return ""

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
        user=self.main.config.GetVar("xmlrpc_username")
        passwd=self.main.config.GetVar("xmlrpc_password")
        
        if self.main.name == "TcosVolumeManager":
            user=self.main.xauth.get_cookie()
            passwd=self.main.xauth.get_hostname()
            if user == None:
                print_debug ( "GetSoundInfo() error loading cookie info" )
                return None
            print_debug ( "GetSoundInfo() cookie=%s hostname=%s" %(user, passwd) )

        if not self.connected:
            print_debug ( "GetSoundInfo() NO CONNECTION" )
            return None

        try:
            result=self.tc.tcos.sound(mode, " \"%s\" " %(channel), user, passwd ).replace('\n', '')
        except Exception, err:
            print_debug("GetSoundInfo() Exception error: %s"%err)
            return ""

        if result.find('error') == 0:
            print_debug ( "GetSoundInfo(): ERROR, result contains error string!!!\n%s" %(result))
            return ""
        else:
            return result

    def SetSound(self, ip, channel, value, mode="--setlevel"):
        if channel == "":
            return None
        if not self.connected:
            print_debug ( "SetSound() NO CONNECTION" )
            return None
        user=self.main.config.GetVar("xmlrpc_username")
        passwd=self.main.config.GetVar("xmlrpc_password")
        
        if self.main.name == "TcosVolumeManager":
            user=self.main.xauth.get_cookie()
            passwd=self.main.xauth.get_hostname()
            if user == None:
                print_debug ( "SetSound() error loading cookie info" )
                return None
            print_debug ( "SetSound() cookie=%s hostname=%s" %(user, passwd) )

        try:
            result=self.tc.tcos.sound(mode, " \"%s\" \"%s\" " %(channel,value), user, passwd).replace('\n', '')
        except Exception, err:
            print_debug("SetSound() Exception error: %s"%err)
            return ""

        if result.find('error') == 0:
            print_debug ( "SetSound(): ERROR, result contains error string!!!\n%s" %(result))
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
        # wait for other petitions
        self.wait()
        # lock process 
        self.lock=True
        # don't fail if timeout
        try:
            result=self.tc.tcos.devices(mode, " \"%s\" " %(device), \
                                       xauth_cookie, \
                                       remote_hostname ).replace('\n', '')
            self.lock=False
            if "error" in result:
                print_debug ( "GetDevicesInfo(device=%s, mode=%s): ERROR, result contains error string!!!\n%s" %(device, mode, result))
            return result
        except Exception, err:
            self.lock=False
            print_debug("GetDevicesInfo(device=%s, mode=%s) EXCEPTION getting info err=%s"%(device, mode, err) )
            return ""

    def lockscreen(self, ip=None):
        if ip: self.newhost(ip)
        if self.isPortListening(self.ip, shared.xmlremote_port):
            try:
                self.tc.tcos.lockscreen( \
                    self.main.config.GetVar("xmlrpc_username"), \
                    self.main.config.GetVar("xmlrpc_password"))
                return True
            except Exception, err:
                print_debug ("lockscreen() Exception, error: %s" %err)
                pass
        return False
        
    def unlockscreen(self, ip=None):
        if ip: self.newhost(ip)
        if self.isPortListening(self.ip, shared.xmlremote_port):
            try:
                self.tc.tcos.unlockscreen(\
                    self.main.config.GetVar("xmlrpc_username"), \
                    self.main.config.GetVar("xmlrpc_password"))
                return True
            except Exception, err:
                print_debug ("unlockscreen() Exception, error: %s" %err)
                pass
        return False
    
    def lockcontroller(self, action, ip=None):
        if ip: self.newhost(ip)
        if self.isPortListening(self.ip, shared.xmlremote_port):
            try:
                self.tc.tcos.lockcontroller("%s" %action, \
                    self.main.config.GetVar("xmlrpc_username"), \
                    self.main.config.GetVar("xmlrpc_password"))
                return True
            except Exception, err:
                print_debug ("lockcontroller() Exception, error: %s" %err)
                pass
        return False
        
    def unlockcontroller(self, action, ip=None):
        if ip: self.newhost(ip)
        if self.isPortListening(self.ip, shared.xmlremote_port):
            try:
                self.tc.tcos.unlockcontroller("%s" %action, \
                    self.main.config.GetVar("xmlrpc_username"), \
                    self.main.config.GetVar("xmlrpc_password"))
                return True
            except Exception, err:
                print_debug ("unlockcontroller() Exception, error: %s" %err)
                pass
        return False

    def status_lockscreen(self, ip=None):
        if ip: self.newhost(ip)
        if self.isPortListening(self.ip, shared.xmlremote_port):
            #self.login ()
            result=self._ParseResult(self.GetStatus("lockscreen"))
            print_debug ( "lockscreen() %s" %(result) )
            return result
        return False
    
    
        
    def screenshot(self, size="65"):
        print_debug ( "screenshot() size=%s" %(size) )
        try:
            result=self._ParseResult( self.tc.tcos.screenshot(\
                     "%s" %(size),\
                     self.main.config.GetVar("xmlrpc_username"), \
                     self.main.config.GetVar("xmlrpc_password")) )
                     
            print_debug ( "screenshot(size=%s percent) %s done" %(size, result) )
            return True
        except Exception, err:
            print_debug ("screenshot() Exception, error: %s" %err)
            return False
        
        
    def vnc(self, action, ip, *args):
        self.newhost(ip)
        if action == "genpass":
            passwd=args
            return self.tc.tcos.vnc("genpass", "%s /tmp/.tcosvnc" %passwd, \
                                self.main.config.GetVar("xmlrpc_username"), \
                                self.main.config.GetVar("xmlrpc_password") )
        elif action == "startserver":
            return self.tc.tcos.vnc("startserver", "/tmp/.tcosvnc", \
                                self.main.config.GetVar("xmlrpc_username"), \
                                self.main.config.GetVar("xmlrpc_password") )
        
        elif action == "stopserver":
            return self.tc.tcos.vnc("stopserver", "",\
                                self.main.config.GetVar("xmlrpc_username"), \
                                self.main.config.GetVar("xmlrpc_password") )
        
        elif action == "startclient":
            server_ip=args
            return self.tc.tcos.vnc("startclient", "%s /tmp/.tcosvnc" %server_ip, \
                                self.main.config.GetVar("xmlrpc_username"), \
                                self.main.config.GetVar("xmlrpc_password") )
        
        elif action == "stopclient":
            return self.tc.tcos.vnc("stopclient", "", \
                                self.main.config.GetVar("xmlrpc_username"), \
                                self.main.config.GetVar("xmlrpc_password") )
            
    def rtp(self, action, ip, broadcast=None):
        self.newhost(ip)
        if action == "startrtp":
            return self.tc.tcos.rtp("startrtp", broadcast, \
                                self.main.config.GetVar("xmlrpc_username"), \
                                self.main.config.GetVar("xmlrpc_password") )
                                
        elif action == "stoprtp":
            return self.tc.tcos.rtp("stoprtp", "", \
                                self.main.config.GetVar("xmlrpc_username"), \
                                self.main.config.GetVar("xmlrpc_password") )
    
    def vlc(self, ip, volume, lock):
        self.newhost(ip)
        return self.tc.tcos.vlc("%s" %volume, "%s" %lock, \
                            self.main.config.GetVar("xmlrpc_username"), \
                            self.main.config.GetVar("xmlrpc_password") )
    
if __name__ == '__main__':
    shared.debug = True
    app=TcosXmlRpc (None)
    
    
    if app.isPortListening("192.168.0.3", "80"):
        print "80 is listening"
    else:
        print "80 is NOT listening"
        
    if app.isPortListening("192.168.0.3", "8998"):
        print "8998 is listening"
    else:
        print "8998 is NOT listening"
    
    #if app.isPortListening("192.168.0.10", "8998"):
    #    print "8998 is listening"
    #else:
    #    print "8998 is NOT listening"
    #start=time()
    #print_debug ("TCOS_VERSION:  %s" %(app.GetVersion()) ) 
    #howmany(start, "get version info")
    
    start=time()
    app.newhost("192.168.0.3")
    print_debug ("TCOS_«tilda»_STATUS:  %s" %(app.GetStatus("tilda")) )
    howmany(start, "get status of tilda")
    
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
