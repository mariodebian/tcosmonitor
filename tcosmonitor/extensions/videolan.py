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

import os
import gtk
import subprocess
import signal

def print_debug(txt):
    if shared.debug:
        print "%s::%s" % ("extensions::videolan", txt)
    return


class VideoOne(TcosExtension):
    def register(self):
        self.vlc_count={}
        self.main.classview.class_external_video=self.video_external
        self.main.actions.button_action_video=self.video_all

        self.main.menus.register_simple( _("Send Audio/Video broadcast") , "menu_broadcast.png", 2, self.video_one, "video")
        self.main.menus.register_all( _("Send Audio/Video broadcast") , "menu_broadcast.png", 2, self.video_all, "video")
        


    def video_external(self, filename):
        if self.main.classview.ismultiple():
            if not self.get_all_clients():
                return
        elif not self.get_client():
            return
        # action sent by vidal_joshur at gva dot es
        # start video broadcast mode
        # Stream to single client unicast
        eth=self.main.config.GetVar("network_interface")
        
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg ( _("Can't send video broadcast, user is not logged") )
            return
                    
        str_scapes=[" ", "(", ")", "*", "!", "?", "\"", "`", "[", "]", "{", "}", ";", ":", ",", "=", "$"]
        lock="disable"
        volume="85"
        
        if self.main.pref_vlc_method_send.get_active() == 0:
            vcodec=shared.vcodecs[0]
            venc=shared.vencs[0]
            acodec=shared.acodecs[0]
            aenc=shared.aencs[0]
            access=shared.accesss[0]
            mux=shared.muxs[0]
        elif self.main.pref_vlc_method_send.get_active() == 1:
            vcodec=shared.vcodecs[1]
            venc=shared.vencs[0]
            acodec=shared.acodecs[0]
            aenc=shared.aencs[0]
            access=shared.accesss[0]
            mux=shared.muxs[0]
        elif self.main.pref_vlc_method_send.get_active() == 2:
            vcodec=shared.vcodecs[2]
            venc=shared.vencs[1]
            acodec=shared.acodecs[0]
            aenc=shared.aencs[0]
            access=shared.accesss[0]
            mux=shared.muxs[0]
        elif self.main.pref_vlc_method_send.get_active() == 3:
            vcodec=shared.vcodecs[3]
            venc=shared.vencs[2]
            acodec=shared.acodecs[1]
            aenc=shared.aencs[1]
            access=shared.accesss[1]
            mux=shared.muxs[1]
        elif self.main.pref_vlc_method_send.get_active() == 4:
            vcodec=shared.vcodecs[1]
            venc=shared.vencs[0]
            acodec=shared.acodecs[1]
            aenc=shared.aencs[1]
            access=shared.accesss[1]
            mux=shared.muxs[1]
        
        if access == "udp":
            max_uip=255
            uip=0
            while uip <= max_uip:
                uip_cmd="239.254.%s.0" %(uip)
                cmd=("LC_ALL=C LC_MESSAGES=C netstat -tapun 2>/dev/null | grep -c %s" %(uip_cmd) )
                print_debug("Check broadcast ip %s." %(uip_cmd) )
                output=self.main.common.exe_cmd(cmd)
                uip+=1
                if output == "0":
                    print_debug("Broadcast ip found: %s" %(uip_cmd))
                    ip_broadcast="%s:1234" %uip_cmd
                    break
                elif uip == max_uip:
                    print_debug("Not found an available broadcast ip")
                    return
        else:
            max_uip=50255
            uip=50000
            while uip <= max_uip:
                uip_cmd=":%s" %(uip)
                cmd=("LC_ALL=C LC_MESSAGES=C netstat -tapun 2>/dev/null | grep -c %s" %(uip_cmd) )
                print_debug("Check broadcast ip %s." %(uip_cmd) )
                output=self.main.common.exe_cmd(cmd)
                uip+=1
                if output == "0":
                    print_debug("Broadcast ip found: %s" %(uip_cmd))
                    ip_broadcast=uip_cmd
                    uip_cmd=""
                    break
                elif uip == max_uip:
                    print_debug("Not found an available broadcast ip")
                    return

        if uip_cmd != "":
            result = self.main.localdata.Route("route-add", uip_cmd, "255.255.255.0", eth)
            if result == "error":
                print_debug("Add multicast-ip route failed")
                return
                
        if filename.find(" ") != -1:
            msg=_("Not allowed white spaces in \"%s\".\nPlease rename it." %os.path.basename(filename) )
            shared.info_msg( msg )
            return
            
        if access == "udp":
            remote_cmd_standalone="vlc udp://@%s --udp-caching=1000 --aout=alsa --brightness=2.000000 --no-x11-shm --no-xvideo-shm --volume=300 --fullscreen --aspect-ratio=4:3 --loop" %(ip_broadcast)
            remote_cmd_thin="vlc udp://@%s --udp-caching=1000 --aout=alsa --brightness=2.000000 --no-x11-shm --no-xvideo-shm --volume=300 --aspect-ratio=4:3 --loop" %(ip_broadcast)
            
        p=subprocess.Popen(["vlc", "file://%s" %filename, "--sout=#duplicate{dst=display{delay=1000},dst=\"transcode{vcodec=%s,venc=%s,acodec=%s,aenc=%s,vb=800,ab=112,channels=2,soverlay}:standard{access=%s,mux=%s,dst=%s}\"}" %(vcodec, venc, acodec, aenc, access, mux, ip_broadcast), "--miface=%s" %eth, "--ttl=12", "--brightness=2.000000", "--no-x11-shm", "--no-xvideo-shm"], shell=False, bufsize=0, close_fds=True)
            
        self.main.write_into_statusbar( _("Waiting for start video transmission...") )
            
        #msg=_("First select the DVD chapter or play movie\nthen press enter to send client..." )
        #shared.info_msg( msg )
            
        # check if vlc is running or fail like check ping in demo mode
        running = p.poll() is None
        if not running:
            self.main.write_into_statusbar( _("Error while exec app"))
            return
            
        #msg=_( "Lock keyboard and mouse on client?" )
        #if shared.ask_msg ( msg ):
        #    lock="enable"
                
        newusernames=[]
            
        for user in self.connected_users:
            if user.find(":") != -1:
                # we have a standalone user...
                usern, ip = user.split(":")
                self.main.xmlrpc.newhost(ip)
                if access == "http":
                    server=self.main.xmlrpc.GetStandalone("get_server")
                    remote_cmd_standalone="vlc http://%s%s --aout=alsa --brightness=2.000000 --no-x11-shm --no-xvideo-shm --volume=300 --fullscreen --aspect-ratio=4:3 --http-reconnect --loop" %(server, ip_broadcast)
                self.main.xmlrpc.DBus("exec", remote_cmd_standalone )
            else:
                newusernames.append(user)
                        
        if access == "http":
            remote_cmd_thin="vlc http://localhost%s --aout=alsa --brightness=2.000000 --no-x11-shm --no-xvideo-shm --volume=300 --aspect-ratio=4:3 --http-reconnect --loop" % (ip_broadcast)
                    
        result = self.main.dbus_action.do_exec( newusernames, remote_cmd_thin )
            
        if not result:
            shared.error_msg ( _("Error while exec remote app:\nReason:%s") %( self.main.dbus_action.get_error_msg() ) )
            
        for client in self.newallclients:
            self.main.xmlrpc.vlc( client, volume, lock )
            
        self.main.write_into_statusbar( _("Running in broadcast video transmission.") )
        # new mode to Stop Button
        if len(self.vlc_count.keys()) != 0:
            count=len(self.vlc_count.keys())-1
            nextkey=self.vlc_count.keys()[count]+1
            self.vlc_count[nextkey]=uip_cmd
        else:
            nextkey=1
            self.vlc_count[nextkey]=uip_cmd
        self.add_progressbox( {"target": "vlc", "pid":p.pid, "lock":lock, "allclients":self.newallclients, "ip":uip_cmd, "iface":eth, "key":nextkey}, _("Running in broadcast video transmission to user %(host)s. Broadcast Nº %(count)s") %{"host":self.connected_users_txt, "count":nextkey} )

    def video_one(self, widget, ip):
        if not self.get_client():
            return
        # action sent by vidal_joshur at gva dot es
        # start video broadcast mode
        # Stream to single client unicast
        eth=self.main.config.GetVar("network_interface")
        
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg ( _("Can't send video broadcast, user is not logged") )
            return
                    
        str_scapes=[" ", "(", ")", "*", "!", "?", "\"", "`", "[", "]", "{", "}", ";", ":", ",", "=", "$"]
        lock="disable"
        volume="85"
        
        if self.main.pref_vlc_method_send.get_active() == 0:
            vcodec=shared.vcodecs[0]
            venc=shared.vencs[0]
            acodec=shared.acodecs[0]
            aenc=shared.aencs[0]
            access=shared.accesss[0]
            mux=shared.muxs[0]
        elif self.main.pref_vlc_method_send.get_active() == 1:
            vcodec=shared.vcodecs[1]
            venc=shared.vencs[0]
            acodec=shared.acodecs[0]
            aenc=shared.aencs[0]
            access=shared.accesss[0]
            mux=shared.muxs[0]
        elif self.main.pref_vlc_method_send.get_active() == 2:
            vcodec=shared.vcodecs[2]
            venc=shared.vencs[1]
            acodec=shared.acodecs[0]
            aenc=shared.aencs[0]
            access=shared.accesss[0]
            mux=shared.muxs[0]
        elif self.main.pref_vlc_method_send.get_active() == 3:
            vcodec=shared.vcodecs[3]
            venc=shared.vencs[2]
            acodec=shared.acodecs[1]
            aenc=shared.aencs[1]
            access=shared.accesss[1]
            mux=shared.muxs[1]
        elif self.main.pref_vlc_method_send.get_active() == 4:
            vcodec=shared.vcodecs[1]
            venc=shared.vencs[0]
            acodec=shared.acodecs[1]
            aenc=shared.aencs[1]
            access=shared.accesss[1]
            mux=shared.muxs[1]
        
        
        if access == "udp": 
            if self.client_type == "tcos":
                max_uip=255
                uip=0
                while uip <= max_uip:
                    uip_cmd="239.254.%s.0" %(uip)
                    cmd=("LC_ALL=C LC_MESSAGES=C netstat -tapun 2>/dev/null | grep -c %s" %(uip_cmd) )
                    print_debug("Check broadcast ip %s." %(uip_cmd) )
                    output=self.main.common.exe_cmd(cmd)
                    uip+=1
                    if output == "0":
                        print_debug("Broadcast ip found: %s" %(uip_cmd))
                        ip_unicast="%s:1234" %uip_cmd
                        break
                    elif uip == max_uip:
                        print_debug("Not found an available broadcast ip")
                        return
                remote_cmd="vlc udp://@%s --udp-caching=1000 --aout=alsa --brightness=2.000000 --no-x11-shm --no-xvideo-shm --volume=300 --aspect-ratio=4:3 --loop" %(ip_unicast)
            else:
                uip_cmd=""
                ip_unicast="%s:1234" %self.main.selected_ip
                remote_cmd="vlc udp://@:1234 --udp-caching=1000 --aout=alsa --brightness=2.000000 --no-x11-shm --no-xvideo-shm --volume=300 --fullscreen --aspect-ratio=4:3 --loop"
        else:
            max_uip=50255
            uip=50000
            while uip <= max_uip:
                uip_cmd=":%s" %(uip)
                cmd=("LC_ALL=C LC_MESSAGES=C netstat -tapun 2>/dev/null | grep -c %s" %(uip_cmd) )
                print_debug("Check broadcast ip %s." %(uip_cmd) )
                output=self.main.common.exe_cmd(cmd)
                uip+=1
                if output == "0":
                    print_debug("Broadcast ip found: %s" %(uip_cmd))
                    ip_unicast=uip_cmd
                    uip_cmd=""
                    break
                elif uip == max_uip:
                    print_debug("Not found an available broadcast ip")
                    return
            if self.client_type == "tcos":
                remote_cmd="vlc http://localhost%s --aout=alsa --brightness=2.000000 --no-x11-shm --no-xvideo-shm --volume=300 --aspect-ratio=4:3 --http-reconnect --loop" %(ip_unicast)
       
        if uip_cmd != "":
            result = self.main.localdata.Route("route-add", uip_cmd, "255.255.255.0", eth)
            if result == "error":
                print_debug("Add multicast-ip route failed")
                return
     
        dialog = gtk.FileChooserDialog(_("Select audio/video file.."),
                            None,
                            gtk.FILE_CHOOSER_ACTION_OPEN,
                            (_("Play DVD"), 1,
                            _("Play SVCD/VCD"), 2,
                            _("Play AudioCD"), 3,
                            gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        self.folder = self._folder = os.environ['HOME']
        dialog.set_current_folder(self.folder)
        filter = gtk.FileFilter()
        filter.set_name("Media Files ( *.avi, *.mpg, *.mpeg, *.mp3, *.wav, etc.. )")
        file_types=["*.avi", "*.mpg", "*.mpeg", "*.ogg", "*.ogm", "*.asf", "*.divx", 
                    "*.wmv", "*.vob", "*.m2v", "*.m4v", "*.mp2", "*.mp4", "*.ac3", 
                    "*.ogg", "*.mp1", "*.mp2", "*.mp3", "*.wav", "*.wma"]
        for elem in file_types:
            filter.add_pattern( elem )
        
        dialog.add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name("All Files")
        filter.add_pattern("*.*")
        dialog.add_filter(filter)
        response = dialog.run()
        if response == gtk.RESPONSE_OK or response == 1 or response == 2 or response == 3:
            
            filename=dialog.get_filename()
            dialog.destroy()
            
            #for scape in str_scapes:
            #    filename=filename.replace("%s" %scape, "\%s" %scape)
            
            if response == gtk.RESPONSE_OK:
                if filename.find(" ") != -1:
                    msg=_("Not allowed white spaces in \"%s\".\nPlease rename it." %os.path.basename(filename) )
                    shared.info_msg( msg )
                    return
                p=subprocess.Popen(["vlc", "file://%s" %filename, "--sout=#duplicate{dst=display{delay=1000},dst=\"transcode{vcodec=%s,venc=%s,acodec=%s,aenc=%s,vb=800,ab=112,channels=2,soverlay}:standard{access=%s,mux=%s,dst=%s}\"}" %(vcodec, venc, acodec, aenc, access, mux, ip_unicast), "--miface=%s" %eth, "--ttl=12", "--brightness=2.000000", "--no-x11-shm", "--no-xvideo-shm"], shell=False, bufsize=0, close_fds=True)
            elif response == 1:
                p=subprocess.Popen(["vlc", "dvdsimple:///dev/cdrom", "--sout=#duplicate{dst=display{delay=700},dst=\"transcode{vcodec=%s,venc=%s,acodec=%s,aenc=%s,vb=800,ab=112,channels=2,soverlay}:standard{access=%s,mux=%s,dst=%s}\"}" %(vcodec, venc, acodec, aenc, access, mux, ip_unicast), "--miface=%s" %eth, "--ttl=12", "--loop", "--brightness=2.000000", "--no-x11-shm", "--no-xvideo-shm"], shell=False, bufsize=0, close_fds=True)
            elif response == 2:
                p=subprocess.Popen(["vlc", "vcd:///dev/cdrom", "--sout=#duplicate{dst=display{delay=1000},dst=\"transcode{vcodec=%s,venc=%s,acodec=%s,aenc=%s,vb=800,ab=112,channels=2,soverlay}:standard{access=%s,mux=%s,dst=%s}\"}" %(vcodec, venc, acodec, aenc, access, mux, ip_unicast), "--miface=%s" %eth, "--ttl=12", "--brightness=2.000000", "--no-x11-shm", "--no-xvideo-shm"], shell=False, bufsize=0, close_fds=True)
            elif response == 3:
                p=subprocess.Popen(["vlc", "cdda:///dev/cdrom", "--sout=#duplicate{dst=display,dst=\"transcode{vcodec=%s,venc=%s,acodec=%s,aenc=%s,vb=200,ab=112,channels=2}:standard{access=%s,mux=%s,dst=%s}\"}" %(vcodec, venc, acodec, aenc, access, mux, ip_unicast), "--miface=%s" %eth, "--ttl=12", "--no-x11-shm", "--no-xvideo-shm"], shell=False, bufsize=0, close_fds=True)
            # exec this app on client
            
            self.main.write_into_statusbar( _("Waiting for start video transmission...") )
            
            msg=_("First select the DVD chapter or play movie\nthen press enter to send clients..." )
            shared.info_msg( msg )
            
            # check if vlc is running or fail like check ping in demo mode
            running = p.poll() is None
            if not running:
                self.main.write_into_statusbar( _("Error while exec app"))
                return
            
            msg=_( "Lock keyboard and mouse on client?" )
            if shared.ask_msg ( msg ):
                lock="enable"
                
            newusernames=[]

            for user in self.connected_users:
                if user.find(":") != -1:
                    # we have a standalone user...
                    if access == "http":
                        server=self.main.xmlrpc.GetStandalone("get_server")
                        remote_cmd="vlc http://%s%s --aout=alsa --brightness=2.000000 --no-x11-shm --no-xvideo-shm --volume=300 --fullscreen --aspect-ratio=4:3 --http-reconnect --loop" %(server, ip_unicast)
                    self.main.xmlrpc.DBus("exec", remote_cmd )
                else:
                    newusernames.append(user)
                    
            result = self.main.dbus_action.do_exec( newusernames, remote_cmd )
            
            if not result:
                shared.error_msg ( _("Error while exec remote app:\nReason:%s") %( self.main.dbus_action.get_error_msg() ) )
            
            self.main.xmlrpc.vlc( self.main.selected_ip, volume, lock )
            
            self.main.write_into_statusbar( _("Running in broadcast video transmission.") )
            # new mode to Stop Button
            if len(self.vlc_count.keys()) != 0:
                count=len(self.vlc_count.keys())-1
                nextkey=self.vlc_count.keys()[count]+1
                self.vlc_count[nextkey]=uip_cmd
            else:
                nextkey=1
                self.vlc_count[nextkey]=uip_cmd
            self.add_progressbox( {"target": "vlc", "pid":p.pid, "lock":lock, "allclients":self.newallclients, "ip":uip_cmd, "iface":eth, "key":nextkey}, _("Running in broadcast video transmission to user %(host)s. Broadcast Nº %(count)s") %{"host":self.connected_users_txt, "count":nextkey} )
        else:
            dialog.destroy()

    def on_progressbox_click(self, widget, args, box):
        box.destroy()
        print_debug("on_progressbox_click() widget=%s, args=%s, box=%s" %(widget, args, box) )
        
        if not args['target']: return

        self.main.stop_running_actions.remove(widget)
        
        if args['target'] == "vlc":
            del self.vlc_count[args['key']]
            if args['ip'] != "":
                result = self.main.localdata.Route("route-del", args['ip'], "255.255.255.0", args['iface'])
                if result == "error":
                    print_debug("Del multicast-ip route failed")
            connected_users=[]
            for client in args['allclients']:
                self.main.localdata.newhost(client)
                if self.main.localdata.IsLogged(client):
                    if args['lock'] == "enable": self.main.xmlrpc.unlockcontroller("lockvlc", client)
                    connected_users.append(self.main.localdata.GetUsernameAndHost(client))
            
            newusernames=[]
                      
            for user in connected_users:
                if user.find(":") != -1:
                    # we have a standalone user... in some cases or after much time need SIGKILL vlc
                    usern, ip = user.split(":")
                    self.main.xmlrpc.newhost(ip)
                    self.main.xmlrpc.DBus("killall", "-s KILL vlc" )
                else:
                    newusernames.append(user)
                    
            result = self.main.dbus_action.do_killall( newusernames , "-s KILL vlc" )
            
            if "pid" in args:
                os.kill(args['pid'], signal.SIGKILL) 
            else:
                self.main.common.exe_cmd("killall -s KILL vlc", verbose=0, background=True)
            self.main.write_into_statusbar( _("Video broadcast stopped.") )


    def video_all(self, *args):
        if not self.get_all_clients():
            return
        # action sent by vidal_joshur at gva dot es
        # start video broadcast mode
        # search for connected users
        # Stream to multiple clients
        eth=self.main.config.GetVar("network_interface")
        
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg( _("No users logged.") )
            return
                    
        str_scapes=[" ", "(", ")", "*", "!", "?", "\"", "`", "[", "]", "{", "}", ";", ":", ",", "=", "$"]
        
        if self.main.pref_vlc_method_send.get_active() == 0:
            vcodec=shared.vcodecs[0]
            venc=shared.vencs[0]
            acodec=shared.acodecs[0]
            aenc=shared.aencs[0]
            access=shared.accesss[0]
            mux=shared.muxs[0]
        elif self.main.pref_vlc_method_send.get_active() == 1:
            vcodec=shared.vcodecs[1]
            venc=shared.vencs[0]
            acodec=shared.acodecs[0]
            aenc=shared.aencs[0]
            access=shared.accesss[0]
            mux=shared.muxs[0]
        elif self.main.pref_vlc_method_send.get_active() == 2:
            vcodec=shared.vcodecs[2]
            venc=shared.vencs[1]
            acodec=shared.acodecs[0]
            aenc=shared.aencs[0]
            access=shared.accesss[0]
            mux=shared.muxs[0]
        elif self.main.pref_vlc_method_send.get_active() == 3:
            vcodec=shared.vcodecs[3]
            venc=shared.vencs[2]
            acodec=shared.acodecs[1]
            aenc=shared.aencs[1]
            access=shared.accesss[1]
            mux=shared.muxs[1]
        elif self.main.pref_vlc_method_send.get_active() == 4:
            vcodec=shared.vcodecs[1]
            venc=shared.vencs[0]
            acodec=shared.acodecs[1]
            aenc=shared.aencs[1]
            access=shared.accesss[1]
            mux=shared.muxs[1]
        
        if access == "udp":
            max_uip=255
            uip=0
            while uip <= max_uip:
                uip_cmd="239.254.%s.0" %(uip)
                cmd=("LC_ALL=C LC_MESSAGES=C netstat -tapun 2>/dev/null | grep -c %s" %(uip_cmd) )
                print_debug("Check broadcast ip %s." %(uip_cmd) )
                output=self.main.common.exe_cmd(cmd)
                uip+=1
                if output == "0":
                    print_debug("Broadcast ip found: %s" %(uip_cmd))
                    ip_broadcast="%s:1234" %uip_cmd
                    break
                elif uip == max_uip:
                    print_debug("Not found an available broadcast ip")
                    return
        else:
            max_uip=50255
            uip=50000
            while uip <= max_uip:
                uip_cmd=":%s" %(uip)
                cmd=("LC_ALL=C LC_MESSAGES=C netstat -tapun 2>/dev/null | grep -c %s" %(uip_cmd) )
                print_debug("Check broadcast ip %s." %(uip_cmd) )
                output=self.main.common.exe_cmd(cmd)
                uip+=1
                if output == "0":
                    print_debug("Broadcast ip found: %s" %(uip_cmd))
                    ip_broadcast=uip_cmd
                    uip_cmd=""
                    break
                elif uip == max_uip:
                    print_debug("Not found an available broadcast ip")
                    return
        
        lock="disable"
        volume="85"

        if uip_cmd != "":
            result = self.main.localdata.Route("route-add", uip_cmd, "255.255.255.0", eth)
            if result == "error":
                print_debug("Add multicast-ip route failed")
                return

        dialog = gtk.FileChooserDialog(_("Select audio/video file.."),
                           None,
                           gtk.FILE_CHOOSER_ACTION_OPEN,
                           (_("Play DVD"), 1,
                            _("Play SVCD/VCD"), 2,
                            _("Play AudioCD"), 3,
                            gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                            gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        self.folder = self._folder = os.environ['HOME']
        dialog.set_current_folder(self.folder)
        filter = gtk.FileFilter()
        filter.set_name("Media Files ( *.avi, *.mpg, *.mpeg, *.mp3, *.wav, etc.. )")
        file_types=["*.avi", "*.mpg", "*.mpeg", "*.ogg", "*.ogm", "*.asf", "*.divx", 
                    "*.wmv", "*.vob", "*.m2v", "*.m4v", "*.mp2", "*.mp4", "*.ac3", 
                    "*.ogg", "*.mp1", "*.mp2", "*.mp3", "*.wav", "*.wma"]
        for elem in file_types:
            filter.add_pattern( elem )
        
        dialog.add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name("All Files")
        filter.add_pattern("*.*")
        dialog.add_filter(filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK or response == 1 or response == 2 or response == 3:
            
            filename=dialog.get_filename()
            dialog.destroy()
                
            #for scape in str_scapes:
            #    filename=filename.replace("%s" %scape, "\%s" %scape)
            
            if response == gtk.RESPONSE_OK:
                if filename.find(" ") != -1:
                    msg=_("Not allowed white spaces in \"%s\".\nPlease rename it." %os.path.basename(filename) )
                    shared.info_msg( msg )
                    return
                p=subprocess.Popen(["vlc", "file://%s" %filename, "--sout=#duplicate{dst=display{delay=1000},dst=\"transcode{vcodec=%s,venc=%s,acodec=%s,aenc=%s,vb=800,ab=112,channels=2,soverlay}:standard{access=%s,mux=%s,dst=%s}\"}" %(vcodec, venc, acodec, aenc, access, mux, ip_broadcast), "--miface=%s" %eth, "--ttl=12", "--brightness=2.000000", "--no-x11-shm", "--no-xvideo-shm"], shell=False, bufsize=0, close_fds=True)
            elif response == 1:
                p=subprocess.Popen(["vlc", "dvdsimple:///dev/cdrom", "--sout=#duplicate{dst=display{delay=700},dst=\"transcode{vcodec=%s,venc=%s,acodec=%s,aenc=%s,vb=800,ab=112,channels=2,soverlay}:standard{access=%s,mux=%s,dst=%s}\"}" %(vcodec, venc, acodec, aenc, access, mux, ip_broadcast), "--miface=%s" %eth, "--ttl=12", "--loop", "--brightness=2.000000", "--no-x11-shm", "--no-xvideo-shm"], shell=False, bufsize=0, close_fds=True)
            elif response == 2:
                p=subprocess.Popen(["vlc", "vcd:///dev/cdrom", "--sout=#duplicate{dst=display{delay=1000},dst=\"transcode{vcodec=%s,venc=%s,acodec=%s,aenc=%s,vb=800,ab=112,channels=2,soverlay}:standard{access=%s,mux=%s,dst=%s}\"}" %(vcodec, venc, acodec, aenc, access, mux, ip_broadcast), "--miface=%s" %eth, "--ttl=12", "--brightness=2.000000", "--no-x11-shm", "--no-xvideo-shm"], shell=False, bufsize=0, close_fds=True)
            elif response == 3:
                p=subprocess.Popen(["vlc", "cdda:///dev/cdrom", "--sout=#duplicate{dst=display,dst=\"transcode{vcodec=%s,venc=%s,acodec=%s,aenc=%s,vb=200,ab=112,channels=2}:standard{access=%s,mux=%s,dst=%s}\"}" %(vcodec, venc, acodec, aenc, access, mux, ip_broadcast), "--miface=%s" %eth, "--ttl=12", "--no-x11-shm", "--no-xvideo-shm"], shell=False, bufsize=0, close_fds=True)
            # exec this app on client
            
            if access == "udp":
                remote_cmd_standalone="vlc udp://@%s --udp-caching=1000 --aout=alsa --brightness=2.000000 --no-x11-shm --no-xvideo-shm --volume=300 --fullscreen --aspect-ratio=4:3 --loop" %(ip_broadcast)
                remote_cmd_thin="vlc udp://@%s --udp-caching=1000 --aout=alsa --brightness=2.000000 --no-x11-shm --no-xvideo-shm --volume=300 --aspect-ratio=4:3 --loop" %(ip_broadcast)

            self.main.write_into_statusbar( _("Waiting for start video transmission...") )
        
            msg=_("First select the DVD chapter or play movie\nthen press enter to send clients..." )
            shared.info_msg( msg )
            
            # check if vlc is running or fail like check ping in demo mode
            running = p.poll() is None
            if not running:
                self.main.write_into_statusbar( _("Error while exec app"))
                return
            
            msg=_( "Lock keyboard and mouse on clients?" )
            if shared.ask_msg ( msg ):
                lock="enable"
                
            newusernames=[]
            
            for user in self.connected_users:
                if user.find(":") != -1:
                    # we have a standalone user...
                    usern, ip = user.split(":")
                    self.main.xmlrpc.newhost(ip)
                    if access == "http":
                        server=self.main.xmlrpc.GetStandalone("get_server")
                        remote_cmd_standalone="vlc http://%s%s --aout=alsa --brightness=2.000000 --no-x11-shm --no-xvideo-shm --volume=300 --fullscreen --aspect-ratio=4:3 --http-reconnect --loop" %(server, ip_broadcast)
                    self.main.xmlrpc.DBus("exec", remote_cmd_standalone )
                else:
                    newusernames.append(user)
                        
            if access == "http":
                remote_cmd_thin="vlc http://localhost%s --aout=alsa --brightness=2.000000 --no-x11-shm --no-xvideo-shm --volume=300 --aspect-ratio=4:3 --http-reconnect --loop" % (ip_broadcast)
                    
            result = self.main.dbus_action.do_exec( newusernames, remote_cmd_thin )
            
            if not result:
                shared.error_msg ( _("Error while exec remote app:\nReason:%s") %( self.main.dbus_action.get_error_msg() ) )
            
            for client in self.newallclients:
                self.main.xmlrpc.vlc( client, volume, lock )
                
            self.main.write_into_statusbar( _("Running in broadcast video transmission.") )
            # new mode Stop Button
            if len(self.vlc_count.keys()) != 0:
                count=len(self.vlc_count.keys())-1
                nextkey=self.vlc_count.keys()[count]+1
                self.vlc_count[nextkey]=uip_cmd
            else:
                nextkey=1
                self.vlc_count[nextkey]=uip_cmd
            self.add_progressbox( {"target": "vlc", "pid":p.pid, "lock":lock, "allclients": self.newallclients, "ip":uip_cmd, "iface":eth, "key":nextkey}, _("Running in broadcast video transmission. Broadcast Nº %s") %(nextkey) )
        else:
            dialog.destroy()



__extclass__=VideoOne
