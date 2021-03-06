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

import xmlrpclib
from time import time, sleep
import sys
import tcosmonitor.shared
from gettext import gettext as _
import socket

from tcosmonitor.ping import PingPort
# needed for __escape__ function
import xml.sax.saxutils

import traceback


def print_debug(txt):
    if tcosmonitor.shared.debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)


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
        self.sslconnection=False
        self.ports=[]
        self.resethosts()

        self.__dic__= {
             '\"'    :    '´´',
             '\''    :    '´'
                      }
        
        if self.main != None:
            self.cache_timeout=self.main.config.GetVar("cache_timeout")
            self.username=self.main.config.GetVar("xmlrpc_username")
            self.password=self.main.config.GetVar("xmlrpc_password")
            
            if self.username == "" or self.password == "":
                # warn empty username and password 
                if self.main.name == "TcosMonitor":
                    self.main.common.threads_enter("TcosXmlRpc:__init__ no user or password")
                    tcosmonitor.shared.error_msg( _("Username or password are empty,\nplease edit in preferences dialog!") )
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
        if not self.lock:
            return
        i=0
        for i in range(40):
            print_debug("##############  wait() i=%s  ##############"%i)
            if not self.lock:
                return
            sleep(0.1)

    def isPortListening(self, ip, port, force=False):
        """
        check if ip and port is live and running something (using sockets)
        
        """
        if not ip:
            return False
        if not port:
            return False
        
        # this avoid to scan same ip a lot of times, but can give errors FIXME
        if not force and self.lasthost == ip and self.lastport == port and self.aliveStatus == "OPEN":
            print_debug("isPortListening() not scanning again, using lastip=%s lastport=%s OPEN" %(ip, port))
            return True
        elif not force and self.lasthost == ip and self.lastport == port and self.aliveStatus == "CLOSED":
            print_debug("isPortListening() not scanning again, using lastip=%s lastport=%s CLOSED" %(ip, port))
            return False
        
        
        self.aliveStatus=PingPort(ip,port).get_status()
        self.lastport=port
        #print_debug ( "isPortListening() PING PORT DONE status=%s" %(self.aliveStatus) )
        if self.aliveStatus == "OPEN":
            print_debug ( "isPortListening(%s:%s) PinPort => OPEN" %(ip, port))
            return True
        else:
            print_debug ( "isPortListening(%s:%s) PinPort => CLOSED" %(ip, port) )
            return False
        
                
    def newhost(self, ip, nossl=False):
        #print_debug ( "newhost(%s)" %(ip) )
        if not ip:
            print_debug("\n\n##########################################\n\n")
            print_debug("newhost() ip is None")
            print_debug("\n\n##########################################\n\n")
            if tcosmonitor.shared.debug:
                sys.exit(1)
            else:
                return
        self.ip=ip
        self.version=None
        self.logged=None
        cached = None
        force=False
        
        # this avoid to scan same ip a lot of times, but can give errors FIXME
        if self.lasthost == ip and self.connected:
            #print_debug("newhost() not scanning again, using lastip=%s lastport=%s SSL=%s" %(ip,self.lastport, self.sslconnection))
            return True
        
        # change ip, force new
        if self.lasthost != ip:
            self.resethosts()
        
        self.lasthost=ip 
        # reset SSL status too
        self.sslconnection=False
        self.connected=False
        self.lastport=tcosmonitor.shared.xmlremote_port
        
        #print_debug("newhost() enable_sslxmlrpc='%s'" %(self.main.config.GetVar("enable_sslxmlrpc")) )
        
        if self.main.config.GetVar("enable_sslxmlrpc") == 1 and nossl == False:
            print_debug("newhost() SSL enabled, trying to ping %s port" %(tcosmonitor.shared.xmlremote_sslport))
            force=True
            if self.isPortListening(ip, tcosmonitor.shared.xmlremote_sslport):
                print_debug("newhost() SSL enabled **********")
                self.sslconnection=True
        
        if not self.sslconnection:
            if not self.isPortListening(ip, tcosmonitor.shared.xmlremote_port, force):
                print_debug("newhost() SSL disabled, trying to ping %s port" %(tcosmonitor.shared.xmlremote_port))
                self.connected=False
                self.sslconnection=False
                return False
        
        if self.main.config.GetVar("enable_sslxmlrpc") == 1 and self.sslconnection:
            self.url = 'https://%s:%d/RPC2' % (self.ip, tcosmonitor.shared.xmlremote_sslport)
        else:
            self.url = 'http://%s:%d/RPC2' % (self.ip, tcosmonitor.shared.xmlremote_port)
        try:
            # set min socket timeout to 2 secs
            socket.setdefaulttimeout(2)
            self.tc = xmlrpclib.ServerProxy(self.url, verbose=False)
            self.connected=True
            # save socket default timeout
            socket.setdefaulttimeout(tcosmonitor.shared.socket_default_timeout)
            print_debug ( "newhost() tcosxmlrpc running on %s" %(self.url) )
            print_debug( {'conected':self.connected, 'ssl':self.sslconnection, 'ip':self.lasthost, 'port':self.lastport} )
            return True
        except Exception, err:
            print_debug("newhost() ERROR conection unavalaible !!! error: %s"%err)
            self.connected=False
            self.CheckSSL(err)
            return False
        
    def CheckSSL(self, err):
        txt="%s" %err
        if txt.find("SSL2_READ_INTERNAL") != -1 and txt.find("bad mac decode") != -1:
            print_debug("SSL BAD MAC DECODE... Deactivating ssl security layer over xmlrpc.")
            self.main.config.SetVar("enable_sslxmlrpc", 0)
            self.main.config.SaveToFile()
            self.main.xmlrpc.resethosts()
        return True

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
            self.CheckSSL(err)
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
            self.tc.tcos.exe(cmd, \
              self.main.config.GetVar("xmlrpc_username"), \
              self.main.config.GetVar("xmlrpc_password"))
        except Exception, err:
            print_debug("Exe() Exception error %s"%err)
            self.CheckSSL(err)
        
    def Kill(self, app):
        """
        kill a running app in thin client
        """
        print_debug ("Kill() INIT, %s" %(app) )
        if not self.connected:
            print_debug ("Kill() Error, NO CONNECTION!!")
            return None
        
        try:
            self.tc.tcos.kill(app, \
              self.main.config.GetVar("xmlrpc_username"), \
              self.main.config.GetVar("xmlrpc_password"))
        except Exception, err:
            print_debug("Kill() Exception error %s"%err)
            self.CheckSSL(err)
    
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
            self.CheckSSL(err)
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
        server.tcos.info("cpu_model")
        """
        if not self.connected:
            print_debug ( "ReadInfo() NO CONNECTION" )
            return None
        try:
            result=self.tc.tcos.info(string)
        except Exception, err:
            print_debug ( "ReadInfo(%s): ERROR, can't connect to XMLRPC server!!! error %s" %(string, err) )
            self.CheckSSL(err)
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
    

    def GetStandalone(self, item, ingroup=None):
        if item == "get_user":
            if not self.connected:
                print_debug ( "GetStandalone() NO CONNECTION" )
                return tcosmonitor.shared.NO_LOGIN_MSG
            try:
                result=self.tc.tcos.standalone("get_user", "")
            except Exception, err:
                print_debug("GetStandalone(get_user) Exception error: %s"%err)
                self.CheckSSL(err)
                return tcosmonitor.shared.NO_LOGIN_MSG
            
            if result.find('error') == 0:
                return tcosmonitor.shared.NO_LOGIN_MSG
            elif result == "":
                return tcosmonitor.shared.NO_LOGIN_MSG
            else:
                return result
                
        elif item == "get_process":
            try:
                return self.tc.tcos.standalone("get_process", "")
            except Exception, err:
                print_debug("GetStandalone(get_process) Exception error: %s"%err)
                self.CheckSSL(err)
                return ""
        
        elif item == "get_server":
            nossl=self.main.config.GetVar("enable_sslxmlrpc")
            try:
                return self.tc.tcos.standalone("get_server", "%s" %nossl)
            except Exception, err:
                print_debug("GetStandalone(get_server) Exception error %s"%err)
                self.CheckSSL(err)
                return ""
        
        elif item == "get_time":
            try:
                return self.tc.tcos.standalone("get_time", "")
            except Exception, err:
                print_debug("GetStandalone(get_time) Exception error %s"%err)
                self.CheckSSL(err)
                return None
            
        elif item == "get_exclude":
            if not self.connected:
                print_debug ( "GetStandalone() NO CONNECTION" )
                return False
            try:
                result=self.tc.tcos.standalone("get_exclude", "%s" %ingroup)
                if result.find('error') == 0 or result == "" or result == "noexclude":
                    return False
                else:
                    return True
            except Exception, err:
                print_debug("GetStandalone(get_exclude) Exception error %s"%err)
                self.CheckSSL(err)
                return False
            
        else:
            return ""
    
    def __escape__(self, txt):
        return xml.sax.saxutils.escape(txt, self.__dic__)
    
    
    def IsEnabled(self, item):
        if self.main.name in ["TcosVolumeManager", "TcosDevicesNG"]:
            user=self.main.xauth.get_cookie()
            passwd=self.main.xauth.get_hostname()
            if user == None:
                print_debug ( "IsEnabled() error loading cookie info" )
                return False
            print_debug ( "IsEnabled() cookie=%s hostname=%s" %(user, passwd) )
        else:
            user=self.main.config.GetVar("xmlrpc_username")
            passwd=self.main.config.GetVar("xmlrpc_password")
        
        # connect to host
        if not self.connected:
            print_debug ( "IsEnabled() NO CONNECTION" )
            return False
            
        try:
            result=self.tc.tcos.config("--get", item, user, passwd )
        except Exception, err:
            print_debug("IsEnabled(--isenabled) Exception error: %s"%err)
            self.CheckSSL(err)
            return False
        
        if result.find('error') == 0:
            print_debug ( "IsEnabled(): ERROR, result contains error string!!!\n%s" %(result))
            return False
        else:
            print_debug ( "IsEnabled(): result='%s'" %(result))
            if result == "-1" or result == "0":
                return False
            return True
    
    
    def DBus(self, action, data):
        username=self.GetStandalone("get_user")
        remote_user=self.main.config.GetVar("xmlrpc_username")
        remote_passwd=self.main.config.GetVar("xmlrpc_password")
        if action == "mess":
            data=self.__escape__( data )
        cmd="--auth='%s:%s' --type=%s --text='%s' --username=%s" %(remote_user, remote_passwd, action, data, username )
        print_debug ("DBus() cmd=%s" %(cmd) )
        try:
            return self.tc.tcos.dbus(cmd, remote_user, remote_passwd)
        except Exception, err:
            print_debug("DBus Exception error %s"%err)
            self.CheckSSL(err)
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
            result=self.tc.tcos.sound("--showcontrols", "", user, passwd )
        except Exception, err:
            print_debug("GetSoundChannels(--showcontrols) Exception error: %s"%err)
            self.CheckSSL(err)
            return ""

        if result.find('error') == 0:
            print_debug ( "GetSoundChannels(): ERROR, result contains error string!!!\n%s" %(result))
            #self.main.write_into_statusbar( "ERROR: %s" %(result) )
            return ""
        else:
            number=len(result.split('|'))
            return result.split('|')[:number-1]

    def GetSoundChannelsContents(self):
        """
        Exec soundctl.sh with some of these args
            --showcontents          ( return all mixer channels )
        """
        
        if self.main.name == "TcosVolumeManager":
            user=self.main.xauth.get_cookie()
            passwd=self.main.xauth.get_hostname()
            if user == None:
                print_debug ( "GetSoundChannelsContents() error loading cookie info" )
                return []
            print_debug ( "GetSoundChannelsContents() cookie=%s hostname=%s" %(user, passwd) )
        else:
            user=self.main.config.GetVar("xmlrpc_username")
            passwd=self.main.config.GetVar("xmlrpc_password")

        

        if not self.connected:
            print_debug ( "GetSoundChannelsContents() NO CONNECTION" )
            return []
            
        try:
            result=self.tc.tcos.sound("--showcontents", "", user, passwd )
        except Exception, err:
            print_debug("GetSoundChannelsContents(--showcontents) Exception error: %s"%err)
            self.CheckSSL(err)
            return []

        if result.find('error') == 0:
            print_debug ( "GetSoundChannelsContents(): ERROR, result contains error string!!!\n%s" %(result))
            #self.main.write_into_statusbar( "ERROR: %s" %(result) )
            return []
        else:
            channels=[]
            tmp=result.split('#')
            number=len(tmp)
            for i in range(len(tmp)):
                c=tmp[i].split(',')
                if len(c) != 4:
                    print_debug("***NOT CHANNEL*** c=%s"%c)
                    continue
                channels.append( {'name':c[0], 'type': c[1], 'level': c[2], 'mute': c[3]} )
            return channels


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
            result=self.tc.tcos.sound(mode, " \"%s\" " %(channel), user, passwd )
        except Exception, err:
            print_debug("GetSoundInfo() Exception error: %s"%err)
            self.CheckSSL(err)
            return ""

        if result.find('error') == 0:
            print_debug ( "GetSoundInfo(): ERROR, result contains error string!!!\n%s" %(result))
            return ""
        else:
            return result

    def SetSound(self, ip, channel, value, mode="--setlevel"):
        if channel == "":
            return {}
        if not self.connected:
            print_debug ( "SetSound() NO CONNECTION" )
            return {}
        user=self.main.config.GetVar("xmlrpc_username")
        passwd=self.main.config.GetVar("xmlrpc_password")
        
        if self.main.name == "TcosVolumeManager":
            user=self.main.xauth.get_cookie()
            passwd=self.main.xauth.get_hostname()
            if user == None:
                print_debug ( "SetSound() error loading cookie info" )
                return {}
            print_debug ( "SetSound() cookie=%s hostname=%s" %(user, passwd) )

        try:
            result=self.tc.tcos.sound(mode, " \"%s\" \"%s\" " %(channel,value), user, passwd)
            print_debug("SetSound() result=%s"%result)
        except Exception, err:
            print_debug("SetSound() Exception error: %s"%err)
            self.CheckSSL(err)
            return {}

        if result.find('error') == 0:
            print_debug ( "SetSound(): ERROR, result contains error string!!!\n%s" %(result))
            #self.main.write_into_statusbar( "ERROR: %s" %(result) )
            return {}
        else:
            c=result.split(',')
            if len(c) != 4:
                print_debug("***NOT CHANNEL*** c=%s"%c)
                return {}
            return {'name':c[0], 'type': c[1], 'level': c[2], 'mute': c[3]}

    def RestartSoundDaemon(self):
        """
        Exec soundctl.sh  --restartpulse
                  ( return nothing )
        """
        
        if self.main.name == "TcosVolumeManager":
            user=self.main.xauth.get_cookie()
            passwd=self.main.xauth.get_hostname()
            if user == None:
                print_debug ( "RestartSoundDaemon() error loading cookie info" )
                return []
            print_debug ( "RestartSoundDaemon() cookie=%s hostname=%s" %(user, passwd) )
        else:
            user=self.main.config.GetVar("xmlrpc_username")
            passwd=self.main.config.GetVar("xmlrpc_password")
        
        if not self.connected:
            print_debug ( "RestartSoundDaemon() NO CONNECTION" )
            return []
        
        try:
            result=self.tc.tcos.sound("--restartpulse", "", user, passwd )
        except Exception, err:
            print_debug("RestartSoundDaemon (--restartpulse) Exception error: %s"%err)
            return []

        if result.find('error') == 0:
            print_debug ( "RestartSoundDaemon(): ERROR, result contains error string!!!\n%s" %(result))
        return


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
                                       remote_hostname )
            self.lock=False
            if "error" in result:
                print_debug ( "GetDevicesInfo(device=%s, mode=%s): ERROR, result contains error string!!!\n%s" %(device, mode, result))
            return result
        except Exception, err:
            self.lock=False
            print_debug("GetDevicesInfo(device=%s, mode=%s) EXCEPTION getting info err=%s"%(device, mode, err) )
            self.CheckSSL(err)
            return ""

    def lockscreen(self, ip=None):
        if ip: 
            self.newhost(ip)
        if self.isPortListening(self.ip, self.lastport):
            try:
                self.tc.tcos.lockscreen( \
                    self.main.config.GetVar("xmlrpc_username"), \
                    self.main.config.GetVar("xmlrpc_password"))
                return True
            except Exception, err:
                print_debug ("lockscreen() Exception, error: %s" %err)
                self.CheckSSL(err)
        return False
        
    def unlockscreen(self, ip=None):
        if ip:
            self.newhost(ip)
        if self.isPortListening(self.ip, self.lastport):
            try:
                self.tc.tcos.unlockscreen(\
                    self.main.config.GetVar("xmlrpc_username"), \
                    self.main.config.GetVar("xmlrpc_password"))
                return True
            except Exception, err:
                print_debug ("unlockscreen() Exception, error: %s" %err)
                self.CheckSSL(err)
        return False
    
    def lockcontroller(self, action, ip=None):
        if ip:
            self.newhost(ip)
        if self.isPortListening(self.ip, self.lastport):
            try:
                self.tc.tcos.lockcontroller("%s" %action, \
                    self.main.config.GetVar("xmlrpc_username"), \
                    self.main.config.GetVar("xmlrpc_password"))
                return True
            except Exception, err:
                print_debug ("lockcontroller() Exception, error: %s" %err)
                self.CheckSSL(err)
        return False
        
    def unlockcontroller(self, action, ip=None):
        if ip:
            self.newhost(ip)
        if self.isPortListening(self.ip, self.lastport):
            try:
                self.tc.tcos.unlockcontroller("%s" %action, \
                    self.main.config.GetVar("xmlrpc_username"), \
                    self.main.config.GetVar("xmlrpc_password"))
                return True
            except Exception, err:
                print_debug ("unlockcontroller() Exception, error: %s" %err)
                self.CheckSSL(err)
        return False

    def status_lockscreen(self, ip=None):
        if ip:
            self.newhost(ip)
        if self.isPortListening(self.ip, self.lastport):
            #self.login ()
            result=self._ParseResult(self.GetStatus("lockscreen"))
            print_debug ( "lockscreen() %s" %(result) )
            return result
        return False
    
    def tnc(self, action, username, ports=None, ip=None):
        print_debug("tnc() action=%s username=%s ports=%s ip=%s only-ports=%s"%(action, username, ports, ip, tcosmonitor.shared.tnc_only_ports))
        if ip:
            self.newhost(ip)
        try:
            if action == "status":
                return self.tc.tcos.tnc("%s" %action, "", "", "%s" %username, \
                            self.main.config.GetVar("xmlrpc_username"), \
                            self.main.config.GetVar("xmlrpc_password") )
            elif action == "enable-internet":
                return self.tc.tcos.tnc("%s" %action, "--only-ports=%s" %tcosmonitor.shared.tnc_only_ports, "", "%s" %username, \
                            self.main.config.GetVar("xmlrpc_username"), \
                            self.main.config.GetVar("xmlrpc_password"))
            elif action == "disable-internet":
                return self.tc.tcos.tnc("%s" %action, "--only-ports=%s" %tcosmonitor.shared.tnc_only_ports, "%s" %ports, "%s" %username, \
                            self.main.config.GetVar("xmlrpc_username"), \
                            self.main.config.GetVar("xmlrpc_password"))
        except Exception, err:
            print_debug ("tnc() Exception, error: %s" %err)
            self.CheckSSL(err)
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
            self.CheckSSL(err)
            return False

    def getscreenshot(self, size="65"):
        try:
            result=self.tc.tcos.getscreenshot(\
                     "%s" %(size),\
                     self.main.config.GetVar("xmlrpc_username"), \
                     self.main.config.GetVar("xmlrpc_password"))
            
            print_debug ( "getscreenshot(size=%s percent) done result=%s" %(size, result[0]) )
            return result
        except Exception, err:
            print_debug ("getscreenshot() Exception, error: %s" %err)
            self.CheckSSL(err)
            return [False, err]
        
    def vnc(self, action, ip, args=""):
        self.newhost(ip)
        print_debug("vnc(action='%s' ip='%s' args='%s')"%(action, ip, args) )
        try:
            if action == "genpass":
                passwd=args
                return self.tc.tcos.vnc("genpass", "%s /tmp/.tcosvnc" %passwd, \
                                    self.main.config.GetVar("xmlrpc_username"), \
                                    self.main.config.GetVar("xmlrpc_password") )
            elif action == "startserver":
                return self.tc.tcos.vnc("startserver", "/tmp/.tcosvnc", \
                                    self.main.config.GetVar("xmlrpc_username"), \
                                    self.main.config.GetVar("xmlrpc_password") )
            elif action == "startscale":
                size=int(self.main.config.GetVar("miniscrot_size"))
                scale="%sx%s"%(size/100., size/100.)
                return self.tc.tcos.vnc("startscale", "/tmp/.tcosvnc %s"%scale, \
                                    self.main.config.GetVar("xmlrpc_username"), \
                                    self.main.config.GetVar("xmlrpc_password") )
            elif action == "stopserver":
                return self.tc.tcos.vnc("stopserver", "", \
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
        except Exception, err:
            print_debug ("vnc() Exception, error: %s" %err)
            traceback.print_exc(file=sys.stderr)
            self.CheckSSL(err)
            return False
            
    def rtp(self, action, ip, broadcast=None):
        self.newhost(ip)
        try:
            if action == "startrtp-recv":
                return self.tc.tcos.rtp("startrtp-recv", broadcast, \
                                    self.main.config.GetVar("xmlrpc_username"), \
                                    self.main.config.GetVar("xmlrpc_password") )
            elif action == "stoprtp-recv":
                return self.tc.tcos.rtp("stoprtp-recv", "", \
                                    self.main.config.GetVar("xmlrpc_username"), \
                                    self.main.config.GetVar("xmlrpc_password") )
            elif action == "startrtp-send":
                return self.tc.tcos.rtp("startrtp-send", broadcast, \
                                    self.main.config.GetVar("xmlrpc_username"), \
                                    self.main.config.GetVar("xmlrpc_password") )
            elif action == "stoprtp-send":
                return self.tc.tcos.rtp("stoprtp-send", "", \
                                    self.main.config.GetVar("xmlrpc_username"), \
                                    self.main.config.GetVar("xmlrpc_password") )
            elif action == "startrtp-chat":
                return self.tc.tcos.rtp("startrtp-chat", broadcast, \
                                    self.main.config.GetVar("xmlrpc_username"), \
                                    self.main.config.GetVar("xmlrpc_password") )
            elif action == "stoprtp-chat":
                return self.tc.tcos.rtp("stoprtp-chat", "", \
                                    self.main.config.GetVar("xmlrpc_username"), \
                                    self.main.config.GetVar("xmlrpc_password") )
        except Exception, err:
            print_debug ("rtp() Exception, error: %s" %err)
            self.CheckSSL(err)
            return False
    
    def vlc(self, ip, volume, lock):
        self.newhost(ip)
        try:
            return self.tc.tcos.vlc("%s" %volume, "%s" %lock, \
                                self.main.config.GetVar("xmlrpc_username"), \
                                self.main.config.GetVar("xmlrpc_password") )
        except Exception, err:
            print_debug ("vlc() Exception, error: %s" %err)
            self.CheckSSL(err)
            return False
    
    def dpms(self, action, ip=None):
        print_debug("dpms() action=%s ip=%s"%(action, ip))
        if ip: 
            self.newhost(ip)
        if not self.connected:
            return False
        if action == "on" or action == "off" or action == "status":
            try:
                return self.tc.tcos.dpms("%s" %action, \
                            self.main.config.GetVar("xmlrpc_username"), \
                            self.main.config.GetVar("xmlrpc_password") )
            except Exception, err:
                print_debug ("dpms() Exception, error: %s" %err)
                self.CheckSSL(err)
        return False
    
if __name__ == '__main__':
    tcosmonitor.shared.debug = True
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
