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

from tcosmonitor import shared
from tcosmonitor.TcosExtensions import TcosExtension


def print_debug(txt):
    if shared.debug:
        print "%s::%s" % ("extensions::audiortp", txt)
    return


class AudioRTP(TcosExtension):
    def register(self):
        self.rtp_count={}
        self.main.menus.register_all( _("Send my MIC audio") , "menu_rtp.png", 2, self.rtp_all, "conference")
        self.main.menus.register_all( _("Chat audio conference") , "menu_rtp.png", 2, self.rtp_chat, "conference")
        self.main.menus.register_simple( _("Send MIC audio (from this host)") , "menu_rtp.png", 2, self.rtp_simple, "conference")

    def rtp_all(self, *args):
        if not self.get_all_clients():
            return
        # conference mode
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg( _("No users logged.") )
            return

        cmd=("LC_ALL=C LC_MESSAGES=C pactl --version 2>/dev/null | awk '{print $2}' | awk -F\".\" '{if ((int($2) >= 9) && (int($3) >= 10)) printf 1}'")
        output=self.main.common.exe_cmd(cmd)
        if output != "1":
            shared.error_msg( _("Your pulseaudio server is too old.\nIs required pulseaudio version >= 0.9.10") )
            return
        
        msg=_( _("Do you want to start conference mode the following users:%s?" )%(self.newallclients_txt) )
                                                
        if not shared.ask_msg ( msg ):
            return

        eth=self.main.config.GetVar("network_interface")
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
        result = self.main.localdata.Route("route-add", ip_broadcast, "255.255.255.0", eth)
        if result == "error":
            print_debug("Add multicast-ip route failed")
            return
        output = self.main.common.exe_cmd("pactl load-module module-rtp-send destination=%s rate=11025 channels=2 port=1234" %ip_broadcast)
                    
        self.main.write_into_statusbar( _("Waiting for start conference mode...") )
                    
        total=0
        for client in self.newallclients:
            self.main.xmlrpc.rtp("startrtp-recv", client, ip_broadcast )
            total+=1
        
        if total < 1:
            self.main.write_into_statusbar( _("No users logged.") )
            # kill x11vnc
            self.main.common.exe_cmd("pactl unload-module %s" %output)
            result = self.main.localdata.Route("route-del", ip_broadcast, "255.255.255.0", eth)
            if result == "error":
                print_debug("Del multicast-ip route failed")
        else:
            self.main.write_into_statusbar( _("Running in conference mode with %s clients.") %(total) )
            # new mode Stop Button
            if len(self.rtp_count.keys()) != 0:
                count=len(self.rtp_count.keys())-1
                nextkey=self.rtp_count.keys()[count]+1
                self.rtp_count[nextkey]=ip_broadcast
            else:
                nextkey=1
                self.rtp_count[nextkey]=ip_broadcast
            self.add_progressbox( {"target": "rtp", "pid":output, "allclients":self.newallclients, "ip":"", "ip_broadcast":ip_broadcast, "iface":eth, "key":nextkey}, _("Running in conference mode from server. Conference Nº %d") %(nextkey) )


    def rtp_simple(self, widget, ip):
        if not self.get_client():
            return
        
        # conference mode
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg( _("Can't start conference mode, user is not logged") )
            return
        
        cmd=("LC_ALL=C LC_MESSAGES=C pactl --version 2>/dev/null | awk '{print $2}' | awk -F\".\" '{if ((int($2) >= 9) && (int($3) >= 10)) printf 1}'")
        output=self.main.common.exe_cmd(cmd)
        if output != "1":
            shared.error_msg( _("Your pulseaudio server is too old.\nIs required pulseaudio version >= 0.9.10") )
            return
            
        msg=_( _("Do you want conference mode from %s?" ) %(self.host) )
        if not shared.ask_msg ( msg ): return

        if self.main.listview.isactive() and self.main.config.GetVar("selectedhosts") == 1:
            self.allclients=self.main.listview.getmultiple()
            if len(self.allclients) == 0:
                msg=_( _("No clients selected, do you want to select all?" ) )
                if shared.ask_msg ( msg ):
                    allclients=self.main.localdata.allclients
        else:
            # get all clients connected
            self.allclients=self.main.localdata.allclients
        
        # Allow one client    
        # if len(self.allclients) == 0: return

        eth=self.main.config.GetVar("network_interface")
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
        result = self.main.localdata.Route("route-add", ip_broadcast, "255.255.255.0", eth)
        if result == "error":
            print_debug("Add multicast-ip route failed")
            return

        #self.main.xmlrpc.newhost(ip)
        self.main.xmlrpc.rtp("startrtp-send", ip, ip_broadcast )
        self.main.write_into_statusbar( _("Waiting for start conference mode from host %s...") %(self.host) )
            
        output = self.main.common.exe_cmd("pactl load-module module-rtp-recv sap_address=%s" %ip_broadcast)
                    
        newallclients=[]
        total=1
        for client in self.allclients:
            self.main.localdata.newhost(client)
            if self.main.localdata.IsLogged(client) and client != ip:
                self.main.xmlrpc.rtp("startrtp-recv", client, ip_broadcast )
                total+=1
                newallclients.append(client)
                
        if total < 1:
            self.main.write_into_statusbar( _("No users logged.") )
            self.main.common.exe_cmd("pactl unload-module %s" %output)
            self.main.xmlrpc.rtp("stoprtp-send", ip )
            result = self.main.localdata.Route("route-del", ip_broadcast, "255.255.255.0", eth)
            if result == "error":
                print_debug("Del multicast-ip route failed")
        else:
            self.main.write_into_statusbar( _("Running in conference mode with %s clients.") %(total) )
            # new mode Stop Button
            if len(self.rtp_count.keys()) != 0:
                count=len(self.rtp_count.keys())-1
                nextkey=self.rtp_count.keys()[count]+1
                self.rtp_count[nextkey]=ip_broadcast
            else:
                nextkey=1
                self.rtp_count[nextkey]=ip_broadcast
            self.add_progressbox( {"target": "rtp", "pid":output, "allclients":newallclients, "ip":ip, "ip_broadcast":ip_broadcast, "iface":eth, "key":nextkey}, _("Running in conference mode from host %(host)s. Conference Nº %(count)d") %{"host":self.host, "count":nextkey} )

    def rtp_chat(self, *args):
        if not self.get_all_clients():
            return
        # conference mode
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg( _("No users logged.") )
            return

        cmd=("LC_ALL=C LC_MESSAGES=C pactl --version 2>/dev/null | awk '{print $2}' | awk -F\".\" '{if ((int($2) >= 9) && (int($3) >= 10)) printf 1}'")
        output=self.main.common.exe_cmd(cmd)
        if output != "1":
            shared.error_msg( _("Your pulseaudio server is too old.\nIs required pulseaudio version >= 0.9.10") )
            return
        
        msg=_( _("Do you want to start chat conference mode the following users:%s?" )%(self.newallclients_txt) )
                                                
        if not shared.ask_msg ( msg ):
            return

        eth=self.main.config.GetVar("network_interface")
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
        result = self.main.localdata.Route("route-add", ip_broadcast, "255.255.255.0", eth)
        if result == "error":
            print_debug("Add multicast-ip route failed")
            return
        
        self.main.write_into_statusbar( _("Waiting for start chat conference mode...") )

        output_send=""
        output_recv=""
        msg=_( "Do you want connect to this chat conference now?" )
        if shared.ask_msg ( msg ):
            output_send = self.main.common.exe_cmd("pactl load-module module-rtp-send destination=%s rate=11025 channels=2 port=1234" %ip_broadcast)
            output_recv = self.main.common.exe_cmd("pactl load-module module-rtp-recv sap_address=%s" %ip_broadcast)
                    
        total=0
        for client in self.newallclients:
            self.main.xmlrpc.rtp("startrtp-chat", client, ip_broadcast )
            total+=1
        
        if total < 1:
            self.main.write_into_statusbar( _("No users logged.") )
            # kill x11vnc
            if output_send != "" or output_recv != "":
                self.main.common.exe_cmd("pactl unload-module %s" %output_send)
                self.main.common.exe_cmd("pactl unload-module %s" %output_recv)
            result = self.main.localdata.Route("route-del", ip_broadcast, "255.255.255.0", eth)
            if result == "error":
                print_debug("Del multicast-ip route failed")
        else:
            self.main.write_into_statusbar( _("Running in chat conference mode with %s clients.") %(total) )
            # new mode Stop Button
            if len(self.rtp_count.keys()) != 0:
                count=len(self.rtp_count.keys())-1
                nextkey=self.rtp_count.keys()[count]+1
                self.rtp_count[nextkey]=ip_broadcast
            else:
                nextkey=1
                self.rtp_count[nextkey]=ip_broadcast
            self.add_progressbox( {"target": "rtp-chat", "pid_send":output_send, "pid_recv":output_recv, "allclients":self.newallclients, "ip":"", "ip_broadcast":ip_broadcast, "iface":eth, "key":nextkey}, _("Running in chat conference mode. Conference Nº %d") %(nextkey) )


    def on_progressbox_click(self, widget, args, box):
        box.destroy()
        print_debug("on_progressbox_click() widget=%s, args=%s, box=%s" %(widget, args, box) )
        
        if not args['target']:
            return
        
        if args['target'] == "rtp":
            del self.rtp_count[args['key']]
            if args['ip_broadcast'] != "":
                result = self.main.localdata.Route("route-del", args['ip_broadcast'], "255.255.255.0", args['iface'])
                if result == "error":
                    print_debug("Del multicast-ip route failed")
            for client in args['allclients']:
                self.main.xmlrpc.rtp("stoprtp-recv", client)
            if "pid" in args:
                self.main.common.exe_cmd("pactl unload-module %s" %args['pid'])
            if args['ip'] != "":
                self.main.xmlrpc.rtp("stoprtp-send", args['ip'] )
            self.main.write_into_statusbar( _("Conference mode off.") )
        
        if args['target'] == "rtp-chat":
            del self.rtp_count[args['key']]
            if args['ip_broadcast'] != "":
                result = self.main.localdata.Route("route-del", args['ip_broadcast'], "255.255.255.0", args['iface'])
                if result == "error":
                    print_debug("Del multicast-ip route failed")
            for client in args['allclients']:
                self.main.xmlrpc.rtp("stoprtp-chat", client)
            if args['pid_send'] != "" or args['pid_recv'] != "":
                self.main.common.exe_cmd("pactl unload-module %s" %args['pid_send'])
                self.main.common.exe_cmd("pactl unload-module %s" %args['pid_recv'])
            self.main.write_into_statusbar( _("Chat conference mode off.") )

       
        
__extclass__=AudioRTP
