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

from gettext import gettext as _


import gtk
import os

# needed for get_screenshot
from time import localtime, sleep

from tcosmonitor import shared
from tcosmonitor.TcosExtensions import TcosExtension
from tcosmonitor.ping import PingPort

import gtkvnc
from random import Random
import string

def print_debug(txt):
    if shared.debug:
        print "%s::%s" % ("extensions::livevnc", txt)
    return



class LiveVNC(TcosExtension):
    def register(self):
        self.main.menus.register_all( _("Live view screens with VNC") , "menu_remote.png", 1, self.live_all, "livevnc")
        self.main.livevnc={}
        self.vncpasswd=""
        self.vncxres={}
        self.main.triggers['clean.datatxt']=self.__cleandatatxt
        self.main.stop_liveview_button=None

    ###########  MULTIPLE HOSTS ###############

    def live_all(self, widget):
        if not self.get_all_clients():
            return
        self.vncpasswd=''.join( Random().sample(string.letters+string.digits, 12) )
        
        self.main.worker=shared.Workers(self.main, None, None)
        self.main.worker.set_for_all_action(self.action_for_clients, self.allclients, 'livevnc' )


    def start_action(self, *args):
        print_debug("START_ACTION")
        self.main.datatxt.clean()
        self.main.stop_liveview_button=gtk.Button(_("Stop") )
        self.main.stop_liveview_button.connect("clicked", self.__cleandatatxt, 'force')
        self.main.stop_liveview_button.show()
        
        self.main.datatxt.insert_block( _("Live view of all hosts") )
                    #"""<span> </span><input type='button' name="self.main.stop_liveview_button" />""" )
        self.main.datatxt.insert_html("<br/>")

    def real_action(self, ip, action):
        #print_debug("real_action() ip=%s self.main.livevnc=%s" %(ip, self.main.livevnc) )
        max_wait=10
        
        
        # generate pass on client
        #self.main.xmlrpc.newhost(ip)
        self.main.xmlrpc.vnc("genpass", ip, self.vncpasswd)
        
        
        # start x11vnc
        result=self.main.xmlrpc.vnc("startscale", ip)
        print_debug("real_action() start remote x11vnc result=%s"%result)
        if result.find("error") != -1:
            return
        
        # wait for start
        status = "CLOSED"
        
        wait=0
        while status != "OPEN":
            status=PingPort(ip, 5900).get_status()
            if status == "CLOSED":
                sleep(1)
                wait+=1
            if wait > max_wait:
                break
        
        # start vnc and save in self.main.vnc dict
        self.main.livevnc[ip]=gtkvnc.Display()
        self.main.livevnc[ip].set_credential(gtkvnc.CREDENTIAL_PASSWORD, self.vncpasswd)
        self.main.livevnc[ip].set_credential(gtkvnc.CREDENTIAL_CLIENTNAME, self.main.name)
        
        self.main.livevnc[ip].connect("vnc-auth-credential", self._vnc_auth_cred, ip)
        #self.main.livevnc[ip].connect("size-request", self._force_resize, ip)
        self.main.livevnc[ip].connect("vnc-connected", self._vnc_connected, ip)
        #self.main.livevnc[ip].connect("clicked", self._vnc_clicked, ip)
        # this freeze GUI
        #self.main.livevnc[ip].set_tooltip_text("%s"%ip)
        
        #print dir(self.main.livevnc[ip])
        
        print_debug("real_action() vnc started!!! ")

    def _vnc_clicked(self, vnc, ip):
        print_debug("_vnc_clicked() vnc=%s ip=%s"%(vnc, ip))


    def _vnc_auth_cred(self, *args):
        #print_debug("vnc_auth_cred() args=%s"%args)
        return


    def _force_resize(self, src, size, ip):
        #print_debug("_force_resize() src=%s size=%s ip=%s"%(src, size, ip))
        w,h = src.get_size_request()
        #print "_force_resize() w=%s h=%s"%(w, h)
        if w == -1 or h == -1:
            print_debug("_force_resize() returning w=%s h=%s ip=%s"%(w, h, ip))
            return
        width=300
        height=200
        if self.vncxres.has_key(ip):
            # cached data
            width=self.vncxres[ip][0]
            height=self.vncxres[ip][1]
        else:
            self.vncxres[ip]=[width, height]
            try:
                screensize=self.main.xmlrpc.ReadInfo("screensize")
                if screensize != '':
                    width=int(screensize.split('x')[0]) * 100 / int(self.main.config.GetVar("miniscrot_size"))
                    height=int(screensize.split('x')[1]) * 100 / int(self.main.config.GetVar("miniscrot_size"))
                    self.vncxres[ip]=[width, height]
                print_debug("_force_resize() RESIZE w=%s h=%s"%(width, height))
            except Exception, err:
                print_debug("_force_resize() Exception err=%s"%err)
                width=300
                height=200
                self.vncxres[ip]=[width, height]
        self.main.livevnc[ip].set_size_request(self.vncxres[ip][0], self.vncxres[ip][1])


    def _vnc_connected(self, vnc, ip):
        print_debug("_vnc_connected() vnc=%s livevnc[ip]=%s ip=%s"%(vnc, self.main.livevnc[ip], ip))
        self.main.livevnc[ip].show()
        self.main.livevnc[ip].realize()


    def finish_action(self, *args):
        for ip in self.main.livevnc:
            #self.main.livevnc[ip]
            self.main.datatxt.insert_html( 
                 "<span style='background-color:#f3d160'>" +
                 "\n\t<livevnc ip='%s' objdict='livevnc' title='%s' title_rotate='90'/> " %(ip, ip) +
                 "<span style='background-color:#f3d160; color:#f3d160'>__</span>\n</span>"+
                 "")
            self.main.livevnc[ip].open_host(ip, '5900')
            #self.main.livevnc[ip].set_scaling(True)
            self.main.livevnc[ip].set_read_only(True)
            self.main.livevnc[ip].show()
        # draw widgets
        self.main.datatxt.display()
        stopargs={"target": "livevnc"}
        self.add_progressbox( stopargs, _("Running in LiveView mode") )

    def on_progressbox_click(self, widget, args, box):
        try:
            box.destroy()
        except:
            pass
        self.__cleandatatxt(None, 'force')



    def __cleandatatxt(self, *args):
        # stop all livevnc connections
        for ip in self.main.livevnc:
            print_debug("__cleandatatxt() STOPPING ip=%s"%ip)
            self.main.livevnc[ip].close()
            # stop server (don't wait)
            self.main.xmlrpc.vnc("stopserver", ip )
        self.main.livevnc={}
        
        if len(args) == 2 and args[1] == 'force':
            self.main.datatxt.clean()
            self.main.stop_liveview_button=None



__extclass__=LiveVNC

