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
""" template extension """

from gettext import gettext as _

import shared
#from TcosExtensions import TcosExtension, Error
from TcosExtensions import TcosExtension
#import os
#from random import Random
#from time import sleep
#import string
#import subprocess
#import signal

def print_debug(txt):
    if shared.debug:
        print "%s::%s" % ("extensions::audiortp", txt)
    return


class AudioRTP(TcosExtension):
    def register(self):
        self.main.menus.register_all( _("Send my MIC audio") , "menu_broadcast.png", 2, self.rtp_all, "conference")
        

    def rtp_all(self, *args):
        if not self.get_all_clients():
            return
        # conference mode
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg( _("No users logged.") )
            return
        
        msg=_( _("Do you want to start conference mode the following users:%s?" )%(self.newallclients_txt) )
                                                
        if not shared.ask_msg ( msg ):
            return
        
        max_uip=255
        uip=0
        while uip <= max_uip:
            uip_cmd="239.255.%s.0" %(uip)
            cmd=("LC_ALL=C LC_MESSAGES=C netstat -putan 2>/dev/null | grep -c %s" %(uip_cmd) )
            print_debug("Check broadcast ip %s." %(uip_cmd) )
            output=self.main.common.exe_cmd(cmd)
            uip+=1
            if output == "0":
                print_debug("Broadcast ip found: %s" %(uip_cmd))
                ip_broadcast="%s" %uip_cmd
                break
            elif uip == max_uip:
                print_debug("Not found an available broadcast ip")
                return
            
        output = self.main.common.exe_cmd("pactl load-module module-rtp-send destination=%s loop=1 port=1234" %ip_broadcast)
                    
        self.main.write_into_statusbar( _("Waiting for start conference mode...") )
                    
        total=0
        for client in self.newallclients:
            self.main.xmlrpc.rtp("startrtp", client, ip_broadcast )
            total+=1
        
        if total < 1:
            self.main.write_into_statusbar( _("No users logged.") )
            # kill x11vnc
            self.main.common.exe_cmd("pactl unload-module %s" %output)
        else:
            self.main.write_into_statusbar( _("Running in conference mode with %s clients.") %(total) )
            # new mode Stop Button
            self.add_progressbox( {"target": "rtp", "ip":"", "pid":output, "allclients":self.newallclients}, _("Running in conference mode from server") )


    def on_progressbox_click(self, widget, args, box):
        box.destroy()
        print_debug("on_progressbox_click() widget=%s, args=%s, box=%s" %(widget, args, box) )
        
        if not args['target']:
            return
        
        if args['target'] == "rtp":
            for client in args['allclients']:
                self.main.xmlrpc.newhost(client)
                self.main.xmlrpc.rtp("stoprtp", client)
            if "pid" in args:
                self.main.common.exe_cmd("pactl unload-module %s" %args['pid'])
            self.main.write_into_statusbar( _("Conference mode off.") )
        
__extclass__=AudioRTP
