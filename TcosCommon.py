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

import os
import socket
#import fcntl
#import struct
import pwd
import shared
#import signal
import threading
from subprocess import Popen, PIPE, STDOUT
from gettext import gettext as _

import netifaces

from time import sleep

def print_debug(txt):
    if shared.debug:
        print "%s::%s" % ("TcosCommon", txt)
    return

class TcosCommon:

    def __init__(self, main):
        self.main=main
        self.thread_lock=False
        self.vars={}
        self.extensions={}
        print_debug("__init__()")
        self.theme=None
        pass

    def get_username(self):
        return pwd.getpwuid(os.getuid())[0]

    def get_userid(self):
        return os.getuid()

    def user_in_group(self, group):
        groups=self.exe_cmd("id")
        if group != "":
            if group in groups: return True
            else: return False
        return False
    
    def cleanproc(self, proc):
        try:
            os.waitpid(proc.pid, os.WCONTINUED)
        except os.error, err:
            print_debug("OSError exception: %s" %err)
            pass
            
    def exe_cmd(self, cmd, verbose=1, background=False, lines=0, cthreads=1):
        self.p = Popen(cmd, shell=True, bufsize=0, stdout=PIPE, stderr=STDOUT, close_fds=True)
        
        if self.main.config.GetVar("threadscontrol") == 1 and cthreads == 1:
            try:
                th=threading.Thread(target=self.cleanproc, args=(self.p,) )
                th.setDaemon(1)
                th.start()
            except Exception, err:
                msg= _("ThreadController: Found error executing %(cmd)s\n\nIf problem persist, disable Thread Controller\nin Preferences and report bug.\nError=%(error)s" %{'cmd':cmd, 'error':err})
                print_debug(msg)
                self.threads_enter("TcosCommon:exe_cmd ThreadController error")
                shared.error_msg(msg)
                self.threads_leave("TcosCommon:exe_cmd ThreadController error")
            
            print_debug("Threads count: %s" %threading.activeCount())
        
        if background: return
        
        output=[]
        stdout = self.p.stdout
        if lines == 1:
            return stdout
        for line in stdout.readlines():
            if line != '\n':
                line=line.replace('\n', '')
                output.append(line)
        if len(output) == 1:
            return output[0]
        elif len(output) > 1:
            if verbose==1:
                print_debug ( "exe_cmd(%s) %s" %(cmd, output) )
            return output
        else:
            if verbose == 1:
                print_debug ( "exe_cmd(%s)=None" %(cmd) )
            return []

    def get_ip_address(self, ifname):
        print_debug("get_ip_address() ifname=%s" %(ifname) )
        if not ifname in netifaces.interfaces():
            return None
        ip=netifaces.ifaddresses(ifname)
        if ip.has_key(netifaces.AF_INET):
            return ip[netifaces.AF_INET][0]['addr']
        return None

    def GetAllNetworkInterfaces(self):
        self.vars["allnetworkinterfaces"]=[]
        for dev in netifaces.interfaces():
            if not dev in shared.hidden_network_ifaces:
                self.vars["allnetworkinterfaces"].append(dev)
                ip=netifaces.ifaddresses(dev)
        print_debug ( "GetAllNetworkInterfaces() %s" %( self.vars["allnetworkinterfaces"] ) )
        return self.vars["allnetworkinterfaces"]

    def get_my_local_ip(self, last=True, force=False):
        if force == True or not "local_ip" in self.vars :
            print_debug("get_my_local_ip()")
            self.vars["local_ip"]=[]
            for dev in self.GetAllNetworkInterfaces():
                ip=self.get_ip_address(dev)
                if ip:
                    self.vars["local_ip"].append(ip)
        if last:
            return self.vars["local_ip"][0]
        else:
            return self.vars["local_ip"]

    def get_all_my_ips(self):
        print_debug("get_all_my_ips()")
        if "local_ip" in self.vars:
            return self.vars["local_ip"]
        return self.get_my_local_ip(last=False)

    def get_display(self, ip_mode=True):
        #print_debug("get_display()")
        self.vars["display_host"]=os.environ["DISPLAY"].split(':')[0]
        self.vars["display_hostname"]=self.vars["display_host"]
        self.vars["display_ip"]=self.vars["display_host"]

        # read hostname and ipaddress based on cookie hostname/ip
        old_timeout=socket.getdefaulttimeout()
        socket.setdefaulttimeout(2)
        try:
            if self.vars["display_host"] != "":
                self.vars["display_hostname"]=socket.gethostbyaddr(self.vars["display_host"])[0]
                self.vars["display_ip"]=socket.gethostbyaddr(self.vars["display_host"])[2][0]
                
            else:
                print_debug("get_display() running in local DISPLAY")
                self.vars["display_ip"]=self.get_my_local_ip()
                self.vars["display_hostname"]=socket.gethostbyaddr(self.vars["display_ip"])[0]
        except Exception, err:
            print_debug("get_display() Exception, error=%s"%err)
            pass

        if ip_mode:
            display=self.vars["display_ip"]
        else:
            display=self.vars["display_hostname"]
        
        socket.setdefaulttimeout(old_timeout)
        print_debug ( "get_display() display_host=%s display_hostname=%s display_ip=%s" %(self.vars["display_host"], self.vars["display_hostname"], self.vars["display_ip"]) )
        return display

    def get_extensions(self):
        if "extensions" in self.vars:
            return self.vars["extensions"]
        self.vars["extensions"]=[]
        for ext in os.listdir(shared.EXTENSIONS):
            if ext.endswith('.py') and ext != "__init__.py" and ext != "template.py":
                #print_debug("get_extensions() extension=%s" %ext)
                self.vars["extensions"].append( ext.split(".py")[0] )
        print_debug("get_extensions() all=%s"%self.vars['extensions'])
        return self.vars["extensions"]

    def register_extension(self, ext):
        print_debug("register_extension() ext=%s"%ext)
        tmp=__import__(ext, fromlist=['extensions'])
        # init extension
        self.extensions[ext]=tmp.__extclass__(self.main)
        # call register method
        self.extensions[ext].register()
        

    def init_all_extensions(self):
        """Init all extensions that contains a extension_filter string"""
        self.extensions={}
        for ext in self.get_extensions():
            try:
                self.extensions[ext]=__import__("extensions." + ext)
            except Exception, err:
                print_debug("init_all_extensions() EXCEPTION importing '%s', error=%s"%(ext, err) )
                continue
            print_debug("init_extensions() init '%s'" %(ext))
            self.register_extension( eval("self.extensions[ext]."+ext) )
            #self.init_extension( eval("self.extensions[ext]."+ext) )


    def threads_enter(self, fromtxt=None):
        import gtk
        #print_debug("===> threads_enter() FROM %s"%fromtxt)
        if self.thread_lock:
            self.wait()
        self.thread_lock=True
        gtk.gdk.threads_enter()

    def threads_leave(self, fromtxt=None):
        import gtk
        #print_debug("======> treads_leave() FROM %s"%fromtxt)
        gtk.gdk.threads_leave()
        self.thread_lock=False

    def wait(self):
        """
        wait (max 4 sec) for self.lock == True
        """
        print_debug("\n\nwait() CALLED\n\n")
        if not self.thread_lock: return
        i=0
        for i in range(40):
            print_debug("wait() ************* i=%s  ***************"%i)
            if not self.thread_lock: return
            sleep(0.1)

    def get_icon_theme(self):
        if self.theme: return self.theme
        try:
            import gconf
        except Exception, err:
            print_debug("get_icon_theme() conf module not installed, error=%s"%err)
            return None
        c=gconf.client_get_default()
        self.theme=c.get_string("/desktop/gnome/interface/icon_theme")
        print_debug("get_icon_theme() readed gconf theme=%s"%self.theme)
        return self.theme

if __name__ == '__main__':
    shared.debug=True
    #import sys
    app=TcosCommon(TcosCommon)
    #print app.get_my_local_ip(last=True)
    #print app.get_display()
    #print app.get_all_my_ips()
    app.get_extensions()
    app.init_all_extensions()
    #print app.get_icon_theme()
    #print app.get_all_my_ips()
    #print app.GetAllNetworkInterfaces()
    #print app.get_ip_address('eth0')
    #print app.get_ip_address('eth1')
    #print app.get_ip_address('br0')
    #print app.get_ip_address('br0:0')
