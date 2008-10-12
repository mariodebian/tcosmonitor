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
import gtk

from tcosmonitor import shared
from tcosmonitor.TcosExtensions import TcosExtension
COL_N, COL_ACTIVE,COL_B,COL_BOOL= range(4)

def print_debug(txt):
    if shared.debug:
        print "%s::%s" % ("extensions::audiortp", txt)
    return


class AudioRTP(TcosExtension):
    def register(self):
        self.rtp_count={}
        self.rtp_control_count={}
        self.control_list=False
        self.init_chat()
        self.main.actions.button_action_audio=self.rtp_all
        self.main.actions.button_action_chat=self.rtp_chat
        self.main.actions.button_action_list=self.control_chat
        
        self.main.menus.register_all( _("Send my MIC audio") , "menu_rtp.png", 2, self.rtp_all, "conference")
        self.main.menus.register_all( _("Audio chat conference") , "menu_chat.png", 2, self.rtp_chat, "conference")
        self.main.menus.register_all( _("Audio chat list") , "menu_list.png", 2, self.control_chat, "conference")
        self.main.menus.register_simple( _("Send MIC audio (from this host)") , "menu_rtp.png", 2, self.rtp_simple, "conference")


    def init_chat(self):
        print_debug ("init chat control")
        self.selected_emission=None
        
        self.model=gtk.ListStore(str, gtk.gdk.Pixbuf, str, 'gboolean')
        self.main.chatwindow=self.main.ui.get_widget('chatwindow')
        self.main.chatwindow.connect('delete-event', self.chat_exit )
        
        
        self.main.chatlist = self.main.ui.get_widget('chatlist')
        self.main.chatlist.set_model (self.model)

        cell1 = gtk.CellRendererText ()
        column1 = gtk.TreeViewColumn (_("Emission"), cell1, text = COL_N)
        column1.set_resizable (True)
        column1.set_sort_column_id(COL_N)
        self.main.chatlist.append_column (column1)
        
        cell2 = gtk.CellRendererPixbuf()
        column2 = gtk.TreeViewColumn (_("State"), cell2, pixbuf = COL_ACTIVE)
        self.main.chatlist.append_column (column2)

        cell3 = gtk.CellRendererText ()
        column3 = gtk.TreeViewColumn (_("Channel"), cell3, text = COL_B)
        column3.set_resizable (True)
        column3.set_sort_column_id(COL_B)
        self.main.chatlist.append_column (column3)
        
        self.table_file = self.main.chatlist.get_selection()
        self.table_file.connect("changed", self.on_chat_list_change)
        
        self.main.chat_button_disconnect=self.main.ui.get_widget('button_chat_disconnect')
        self.main.chat_button_disconnect.connect('clicked', self.chat_disconnect)
        
        self.main.chat_button_connect=self.main.ui.get_widget('button_chat_connect')
        self.main.chat_button_connect.connect('clicked', self.chat_connect)
        
        self.main.chat_button_exit=self.main.ui.get_widget('button_exit')
        self.main.chat_button_exit.connect('clicked', self.chat_exit)

        self.main.chat_button_disconnect.set_sensitive(False)
        self.main.chat_button_connect.set_sensitive(False)

        self.main.chatwindow.hide()

    def control_chat(self, *args):
        #if len(self.rtp_count) < 1:
        #    shared.info_msg( _("No active chats to manage") )
        #    return

        self.populate_data(self.rtp_count)
        self.main.chatwindow.show()
        self.control_list=True
        
    def populate_data(self, data):
        self.image_noactive = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'no.png')
        self.image_active = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'ok.png')

        for item in data:
            if data[item] not in self.rtp_control_count.keys():
                continue
            self.new_line=True
            model=self.main.chatlist.get_model()
            model.foreach(self.line_exists, data[item])
            
            if self.new_line:
                self.iter = self.model.append (None)
                name="Chat %s" %item
                self.model.set_value (self.iter, COL_N, name )
                self.model.set_value (self.iter, COL_B, data[item] )
                if len(self.rtp_control_count[data[item]]) < 1:
                    self.model.set_value (self.iter, COL_ACTIVE, self.image_noactive )
                    self.model.set_value (self.iter, COL_BOOL, False )

                else:
                    self.model.set_value (self.iter, COL_ACTIVE, self.image_active )
                    self.model.set_value (self.iter, COL_BOOL, True )

    def control_buttons(self, active):
        if active:
            self.main.chat_button_disconnect.set_sensitive(True)
            self.main.chat_button_connect.set_sensitive(False)
        else:
            self.main.chat_button_disconnect.set_sensitive(False)
            self.main.chat_button_connect.set_sensitive(True)

    def on_chat_list_change (self, data):
        (model, iter) = self.main.chatlist.get_selection().get_selected()
        if not iter:
            self.control_buttons(False)
            return
        self.selected_num=model.get_value(iter,0)
        self.selected_channel=model.get_value(iter, 2)
        self.connected_rtp=model.get_value(iter, 3)
        print_debug("selected_num=%s selected_channel=%s connected=%s" %(self.selected_num, self.selected_channel, self.connected_rtp))
        if self.connected_rtp:
            self.control_buttons(True)
        else:
            self.control_buttons(False)

    def chat_disconnect(self, *args):
        (model, iter) = self.main.chatlist.get_selection().get_selected()
        if not iter:
            self.control_buttons(False)
            return
        self.selected_channel=model.get_value(iter, 2)
        self.main.common.exe_cmd("pactl unload-module %s" %self.rtp_control_count[self.selected_channel][0])
        self.main.common.exe_cmd("pactl unload-module %s" %self.rtp_control_count[self.selected_channel][1])
        self.rtp_control_count[self.selected_channel]=[]
        print_debug("chat_connects %s" %self.rtp_control_count)
        model.foreach(self.line_changer, [self.selected_channel, self.image_noactive, False])
        self.main.chat_button_disconnect.set_sensitive(False)
        self.main.chat_button_connect.set_sensitive(True)
        return True

    def chat_connect(self, *args):
        (model, iter) = self.main.chatlist.get_selection().get_selected()
        if not iter:
            self.control_buttons(False)
            return
        self.selected_channel=model.get_value(iter, 2)
        output_send = self.main.common.exe_cmd("pactl load-module module-rtp-send destination=%s rate=11025 channels=2 port=1234" %self.selected_channel)
        output_recv = self.main.common.exe_cmd("pactl load-module module-rtp-recv sap_address=%s" %self.selected_channel)
        if output_send != "" or output_recv != "":
            self.rtp_control_count[self.selected_channel]=[output_send, output_recv]
            print_debug("chat_connects %s" %self.rtp_control_count)
            model.foreach(self.line_changer, [self.selected_channel, self.image_active, True])
            self.main.chat_button_disconnect.set_sensitive(True)
            self.main.chat_button_connect.set_sensitive(False)
        return True

    def chat_exit(self, *args):
        self.main.chatwindow.hide()
        self.model.clear()
        self.control_list=False
        return True
    
    def line_exists(self, model, path, iter, args):
        ip = args
        # change mac if ip is the same.
        if model.get_value(iter, 2) == ip:
            self.new_line=False
            
    def line_changer(self, model, path, iter, args):
        ip, image, active = args
        # change mac if ip is the same.
        if model.get_value(iter, 2) == ip:
            model.set_value(iter, 1, image)
            model.set_value(iter, 3, active)
            
    def line_delete(self, model, path, iter, args):
        ip = args
        if model.get_value(iter, 2) == ip:
            self.delete_iter=iter
            
    def chat_delete(self, data):
        print_debug("chat_delete() data=%s" %data)
        model=self.main.chatlist.get_model()
        self.delete_iter=None
        model.foreach(self.line_delete, data)
        # delete iter if found
        if self.delete_iter is not None:
            model.remove(self.delete_iter)

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
        
        msg=_( _("Do you want to start audio conference to the following users: %s?" )%(self.connected_users_txt) )
                                                
        if not shared.ask_msg ( msg ):
            return

        remote_msg=_("You have entered in audio conference")
        eth=self.main.config.GetVar("network_interface")
        max_uip=255
        uip=0
        while uip <= max_uip:
            uip_cmd="239.255.%s.0" %(uip)
            cmd=("LC_ALL=C LC_MESSAGES=C netstat -putan 2>/dev/null | grep -c %s" %(uip_cmd) )
            print_debug("Check broadcast ip %s." %(uip_cmd) )
            output=self.main.common.exe_cmd(cmd)
            uip+=1
            if output == "0" and uip_cmd not in self.rtp_count.values():
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
                    
        self.main.write_into_statusbar( _("Waiting for start audio conference...") )
                    
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
            newusernames=[]
            for user in self.connected_users:
                if user.find(":") != -1:
                    # we have a standalone user...
                    usern, ip = user.split(":")
                    self.main.xmlrpc.newhost(ip)
                    self.main.xmlrpc.DBus("mess", remote_msg)
                else:
                    newusernames.append(user)
                    
            self.main.dbus_action.do_message( newusernames, remote_msg )
            self.main.write_into_statusbar( _("Running in audio conference with %s clients.") %(total) )
            # new mode Stop Button
            if len(self.rtp_count.keys()) != 0:
                count=len(self.rtp_count.keys())-1
                nextkey=self.rtp_count.keys()[count]+1
                self.rtp_count[nextkey]=ip_broadcast
            else:
                nextkey=1
                self.rtp_count[nextkey]=ip_broadcast
            self.main.menus.broadcast_count[ip_broadcast]=None
            self.add_progressbox( {"target": "rtp", "pid":output, "allclients":self.newallclients, "ip":"", "ip_broadcast":ip_broadcast, "iface":eth, "key":nextkey}, _("Running in audio conference from server. Conference Nº %s") %(nextkey) )


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
            
        msg=_( _("Do you want audio conference from user %s?" ) %(self.connected_users_txt) )
        if not shared.ask_msg ( msg ): return

        if self.main.listview.isactive() and self.main.config.GetVar("selectedhosts") == 1:
            self.allclients=self.main.listview.getmultiple()
            if len(self.allclients) == 0:
                #msg=_( _("No clients selected, do you want to select all?" ) )
                #if shared.ask_msg ( msg ):
                allclients=self.main.localdata.allclients
        else:
            # get all clients connected
            self.allclients=self.main.localdata.allclients
        
        # Allow one client    
        # if len(self.allclients) == 0: return
        remote_msg=_("You have entered in audio conference from user %s") %self.connected_users_txt
        eth=self.main.config.GetVar("network_interface")
        max_uip=255
        uip=0
        while uip <= max_uip:
            uip_cmd="239.255.%s.0" %(uip)
            cmd=("LC_ALL=C LC_MESSAGES=C netstat -putan 2>/dev/null | grep -c %s" %(uip_cmd) )
            print_debug("Check broadcast ip %s." %(uip_cmd) )
            output=self.main.common.exe_cmd(cmd)
            uip+=1
            if output == "0" and uip_cmd not in self.rtp_count.values():
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
        self.main.write_into_statusbar( _("Waiting for start audio conference from user %s...") %(self.connected_users_txt) )
            
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
            newusernames=[]
            for user in self.connected_users:
                if user.find(":") != -1:
                    # we have a standalone user...
                    usern, ip = user.split(":")
                    self.main.xmlrpc.newhost(ip)
                    self.main.xmlrpc.DBus("mess", remote_msg)
                else:
                    newusernames.append(user)
            self.main.dbus_action.do_message( newusernames, remote_msg )
            self.main.write_into_statusbar( _("Running in audio conference with %s clients.") %(total) )
            # new mode Stop Button
            if len(self.rtp_count.keys()) != 0:
                count=len(self.rtp_count.keys())-1
                nextkey=self.rtp_count.keys()[count]+1
                self.rtp_count[nextkey]=ip_broadcast
            else:
                nextkey=1
                self.rtp_count[nextkey]=ip_broadcast
            self.main.menus.broadcast_count[ip_broadcast]=None
            self.add_progressbox( {"target": "rtp", "pid":output, "allclients":newallclients, "ip":ip, "ip_broadcast":ip_broadcast, "iface":eth, "key":nextkey}, _("Running in audio conference from user %(host)s. Conference Nº %(count)s") %{"host":self.connected_users_txt, "count":nextkey} )

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
        
        msg=_( _("Do you want to start audio chat conference to the following users: %s?" )%(self.connected_users_txt) )
                                                
        if not shared.ask_msg ( msg ):
            return

        remote_msg=_("You have entered in audio chat conference. Participants: %s") %self.connected_users_txt
        eth=self.main.config.GetVar("network_interface")
        max_uip=255
        uip=0
        while uip <= max_uip:
            uip_cmd="239.255.%s.0" %(uip)
            cmd=("LC_ALL=C LC_MESSAGES=C netstat -putan 2>/dev/null | grep -c %s" %(uip_cmd) )
            print_debug("Check broadcast ip %s." %(uip_cmd) )
            output=self.main.common.exe_cmd(cmd)
            uip+=1
            if output == "0" and uip_cmd not in self.rtp_count.values():
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
        
        self.main.write_into_statusbar( _("Waiting for start audio chat conference...") )

        output_send=""
        output_recv=""
        self.rtp_control_count[ip_broadcast]=[]
        msg=_( "Do you want to connect to this audio chat conference now?" )
        if shared.ask_msg ( msg ):
            output_send = self.main.common.exe_cmd("pactl load-module module-rtp-send destination=%s rate=11025 channels=2 port=1234" %ip_broadcast)
            output_recv = self.main.common.exe_cmd("pactl load-module module-rtp-recv sap_address=%s" %ip_broadcast)
            self.rtp_control_count[ip_broadcast]=[output_send, output_recv]
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
            del self.rtp_control_count[ip_broadcast]
            result = self.main.localdata.Route("route-del", ip_broadcast, "255.255.255.0", eth)
            if result == "error":
                print_debug("Del multicast-ip route failed")
        else:
            newusernames=[]
            for user in self.connected_users:
                if user.find(":") != -1:
                    # we have a standalone user...
                    usern, ip = user.split(":")
                    self.main.xmlrpc.newhost(ip)
                    self.main.xmlrpc.DBus("mess", remote_msg)
                else:
                    newusernames.append(user)
            self.main.dbus_action.do_message( newusernames, remote_msg )
            
            self.main.write_into_statusbar( _("Running in audio chat conference with %s clients.") %(total) )
            # new mode Stop Button
            if len(self.rtp_count.keys()) != 0:
                count=len(self.rtp_count.keys())-1
                nextkey=self.rtp_count.keys()[count]+1
                self.rtp_count[nextkey]=ip_broadcast
            else:
                nextkey=1
                self.rtp_count[nextkey]=ip_broadcast
            if self.control_list:
                self.populate_data(self.rtp_count)
            self.main.menus.broadcast_count[ip_broadcast]=None
            self.add_progressbox( {"target": "rtp-chat", "pid_send":output_send, "pid_recv":output_recv, "allclients":self.newallclients, "ip":"", "ip_broadcast":ip_broadcast, "iface":eth, "key":nextkey}, _("Running in audio chat conference. Conference Nº %s") %(nextkey) )

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
                del self.main.menus.broadcast_count[args['ip_broadcast']]
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
                del self.main.menus.broadcast_count[args['ip_broadcast']]
            for client in args['allclients']:
                self.main.xmlrpc.rtp("stoprtp-chat", client)
            if self.rtp_control_count.has_key(args['ip_broadcast']) and len(self.rtp_control_count[args['ip_broadcast']]) > 0:
                self.main.common.exe_cmd("pactl unload-module %s" %self.rtp_control_count[args['ip_broadcast']][0])
                self.main.common.exe_cmd("pactl unload-module %s" %self.rtp_control_count[args['ip_broadcast']][1])
            del self.rtp_control_count[args['ip_broadcast']]
            if self.control_list:
                self.chat_delete(args['ip_broadcast'])
            self.main.write_into_statusbar( _("Chat conference mode off.") )

       
        
__extclass__=AudioRTP
