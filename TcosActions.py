# -*- coding: UTF-8 -*-
##########################################################################
# TcosMonitor writen by MarioDebian <mariodebian@gmail.com>
#
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

from time import time, sleep, localtime
import gobject
import gtk
from gettext import gettext as _
import os


COL_HOST, COL_IP, COL_USERNAME, COL_ACTIVE, COL_LOGGED, COL_BLOCKED, COL_PROCESS, COL_TIME = range(8)
import shared

def print_debug(txt):
    if shared.debug:
        print "%s::%s" %(__name__, txt)

def crono(start, txt):
    print_debug ("crono(), %s get %f seconds" %(txt, (time() - start)) )
    return



class TcosActions:
    def __init__(self, main):
        print_debug ( "__init__()" )
        self.main=main
        self.model=self.main.init.model
        #self.update_hostlist()


    ############################################################################    
    def on_openvolumecontrol_button_click(self, widget, ip):
        print_debug ( "on_openvolumecontrol_button_click() ip=%s" %(ip) )
        cmd="PULSE_SERVER=\"%s\" pavucontrol" %(ip)
        if os.path.isdir("/dev/shm"):
            self.main.exe_cmd( cmd )
        else:
            shared.error_msg ( _("PulseAudio apps need /dev/shm.") )
        
    def on_openvolumemeter_button_click(self, widget, ip):
        print_debug ( "on_openvolumemeter_button_click()  ip=%s" %(ip) )
        cmd="PULSE_SERVER=\"%s\" pavumeter" %(ip)
        if os.path.isdir("/dev/shm"):
            self.main.exe_cmd( cmd )
        else:
            shared.error_msg ( _("PulseAudio apps need /dev/shm.") )
    
    def on_volumemanager_button_click(self, widget, ip):
        print_debug ( "on_volumemanager_button_click() ip=%s" %(ip) )
        cmd="PULSE_SERVER=\"%s\" paman" %(ip)
        if os.path.isdir("/dev/shm"):
            self.main.exe_cmd( cmd )
        else:
            shared.error_msg ( _("PulseAudio apps need /dev/shm.") )

    def on_kill_button_click(self, widget, pid, username):
        print_debug ( "on_kill_button_click() FIXME pid=%s username=%s" %(pid, username) )
        if shared.ask_msg ( _("Are you sure sou want to stop this process?") ):
            print_debug ( "KILL KILL KILL" )
            result = self.main.dbus_action.do_kill( [username] , str(pid) )
            if not result:
                shared.error_msg ( _("Error while killing app:\nReason: %s") %( self.main.dbus_action.get_error_msg() ) )
            else:
                print_debug ( "on_kill_button_click() KILLED ;)" )
                self.get_user_processes(self.main.selected_ip)  

    def on_another_screenshot_button_click(self, widget, ip):
        print_debug ( "on_another_screenshot_button_click() __init__ ip=%s" %(ip) )
        self.main.worker=shared.Worker(self.main, target=self.get_screenshot, args=[ip])
        self.main.worker.start()
        #gobject.timeout_add( 50, self.get_screenshot, ip )   
    
    def on_rightclickmenuone_click(self, menu, number):
        print_debug ( "on_rightclickmenuone_click() => onehost_menuitems[%d]=%s" \
                        % (number, shared.onehost_menuitems[number][0]) )
        self.menu_event_one(number)

    def on_rightclickmenuall_click(self, menu, number):
        print_debug ( "on_rightclickmenuall_click() => allhost_menuitems[%d]=%s" \
                        % (number, shared.allhost_menuitems[number][0]) )
        self.menu_event_all(number)

    def on_preferencesbutton_click(self,widget):
        self.main.pref.show()
    
    def on_aboutbutton_click(self,widget):
        self.main.about.show()
    
    def on_fullscreenbutton_click(self, widget):
        if self.main.is_fullscreen:
            self.main.mainwindow.unfullscreen()
            self.main.is_fullscreen=False
            self.main.fullscreenbutton.set_stock_id("gtk-fullscreen")
        else:
            self.main.mainwindow.fullscreen()
            self.main.is_fullscreen=True
            self.main.fullscreenbutton.set_stock_id("gtk-leave-fullscreen")
    
    def on_downloadallmodules_click(self, widget):
        print_debug ( "FIXME on_downloadallmodules_click() ################" )
        if self.main.selected_ip != None:
            print_debug( "on_downloadallmodules_click() downloading modules for %s" %(self.main.selected_ip) )
            # download allmodules.squashfs and mount it
            self.main.xmlrpc.Exe("useallmodules.sh")
        pass
    
    
    def on_progressbutton_click(self, widget):
        print_debug( "on_progressbutton_click()" )
        
        if not self.main.worker.is_stoped():
            self.main.worker.stop()
            self.main.progressbutton.hide()
        
    def on_pref_ok_button_click(self, widget):
        self.main.config.SaveSettings()
        # refresh pref widgets
        self.main.init.populate_pref()
        print_debug ( "on_pref_ok_button_click() SAVE SETTINGS !!!" )
        self.main.write_into_statusbar ( _("New settings saved.") )
        self.main.pref.hide()
        
    def on_pref_cancel_button_click(self, widget):
        print_debug ( "on_pref_cancel_button_click()" )
        # refresh pref widgets
        self.main.init.populate_pref()
        self.main.pref.hide()        
    
    def on_refreshbutton_click(self,widget):
        self.main.write_into_statusbar ( _("Searching for connected hosts...") )
        
        if self.main.config.GetVar("scan_network_method") == "ping":
            allclients=self.main.localdata.GetAllClients("ping")
            # ping will call populate_hostlist when finish
            return
        else:
            allclients=self.main.localdata.GetAllClients("netstat")
            if len(allclients) == 0:
                self.main.write_into_statusbar ( _("Not connected hosts found.") )
                # clean treeview
                model=self.main.tabla.get_model()
                model.clear()
                return
            self.main.write_into_statusbar ( _("Found %d hosts" ) %len(allclients) )
            # populate_list in a thread
            #gobject.timeout_add( 50, self.actions.populate_hostlist, allclients )
            
            self.main.worker=shared.Workers(self.main, self.populate_hostlist, [allclients] )
            self.main.worker.start()
            return
        
    def on_searchbutton_click(self, widget):
        print_debug ( "on_searchbutton_click()" )
        self.main.search_host(widget)
    
    ############################################################################

    def populate_host_list(self):
        allclients=self.main.localdata.GetAllClients()
        self.populate_hostlist(allclients)
        print_debug ( "POPULATE_HOST_LIST() returning %s" %(self.main.updating) )
        return self.main.updating


    def on_hostlist_click(self, hostlist):
        if self.main.worker_running:
            return
        
        self.main.progressbar.hide()
        (model, iter) = hostlist.get_selected()
        if not iter:
            return
        self.main.selected_host=model.get_value(iter,0)
        self.main.selected_ip=model.get_value(iter, 1)
        
        print_debug ( "on_hostlist_clic() selectedhost=%s selectedip=%s" \
            %(self.main.selected_host, self.main.selected_ip) )
            
        # call to read remote info
        self.main.xmlrpc.newhost(self.main.selected_ip)
        self.main.xmlrpc.ip=self.main.selected_ip
        if not self.main.xmlrpc.isPortListening(self.main.selected_ip, shared.xmlremote_port):
            print_debug ( "on_host_list_click() XMLRPC not running in %s" %(self.main.selected_ip) )
            self.main.write_into_statusbar ( _("Error connecting to tcosxmlrpc in %s") %(self.main.selected_ip) )
            return
        
        print_debug ( "on_host_list_click() AUTH OK" )
        
        self.main.write_into_statusbar ( "" )
        print_debug ( "on_hostlist_click() callig worker to populate in Thread" )
        
        self.main.worker=shared.Workers( self.main,\
                     target=self.populate_datatxt, args=([self.main.selected_ip]) ).start()
        
        return
        
    def askwindow_close(self, widget, event):
        print_debug ( "askwindow_close() closing ask window" )
        self.main.ask.hide()
        return True
    
    def on_ask_exec_click(self, widget):
        app=self.main.ask_entry.get_text()
        if app != "":
            self.exe_app_in_client_display(app)
        return
        
    def on_ask_cancel_click(self, widget):
        self.main.ask.hide()
        self.main.ask_entry.set_text("")
        return
    
    def askfor(self, mode="mess", msg="", users=[]):
        self.ask_usernames=[]
        if len(users) == 0:
            shared.error_msg( _("Clients not connected") )
            return
        else:
            self.ask_usernames=users
        
        if mode == "exec":
            self.main.ask_label.set_markup( _("<b>Exec app in %s user screen</b>" ) %(", ".join(self.ask_usernames)) )
        elif mode == "mess":
            self.main.ask_label.set_markup( _("<b>Send a message to %s</b>" ) %(", ".join(self.ask_usernames)) )
        elif mode == "any":
            self.main.ask_label.set_markup( msg )
        self.ask_mode=mode
        self.main.ask.show()
        return True
    
    
                
    def exe_app_in_client_display(self, arg):
        usernames=self.ask_usernames
        if self.ask_mode == "exec":
            result = self.main.dbus_action.do_exec( usernames , arg )
            if not result:
                shared.error_msg ( _("Error while exec remote app:\nReason: %s") %( self.main.dbus_action.get_error_msg() ) )
            else:
                self.main.ask.hide()
                self.main.ask_entry.set_text("")
        elif self.ask_mode == "mess":
            result = self.main.dbus_action.do_message( usernames , arg)
            if not result:
                shared.error_msg ( _("Error while send message:\nReason: %s") %( self.main.dbus_action.get_error_msg() ) )
            else:
                self.main.ask.hide()
                self.main.ask_entry.set_text("")
                
        dbus_action=None
        self.ask_mode=None
        return 

    def set_progressbar(self, txt, number, show_percent=True):
        percent=int(number*100)
        #print_debug( "set_progressbar() set porc=%f percent=%d%%" %(number, percent) )
        if show_percent:
            self.main.progressbar.set_text("%s (%d %%)" %(txt, percent))
        else:
            self.main.progressbar.set_text("%s" %(txt))
        self.main.progressbar.set_fraction(number)
    
    def update_progressbar(self, number):
        number=float(number)
        if number > 1:
            return
        print_debug( "update_progressbar() set number=%f" %(number) )
        self.main.progressbar.set_fraction(number)
        
    def populate_datatxt(self, ip):
        start1=time()
        print_debug ("populate_datatxt() INIT")
        
        if not self.main.xmlrpc.connected:
            print_debug ( "populate_datatxt(%s) NO CONNECTION" %(ip) )
            crono(start1, "populate_datatxt(%s)" %(ip) )
            return
        
        # dictionary with all data
        tcos_vars={}
        
        self.datatxt = self.main.datatxt
        
        # clear datatxt
        self.datatxt.clean()

        tcos_vars["get_client"] = self.main.xmlrpc.ReadInfo("get_client")
        print_debug ( "Client type=%s" %(tcos_vars["get_client"]) )
        
        # print into statusbar
        gtk.gdk.threads_enter()
        #self.main.write_into_statusbar( _("Connecting with %s to retrieve some info..."  ) %(ip) )
        
        self.main.progressbar.show()
        #self.main.progressbutton.show()
        self.set_progressbar( _("Connecting with %s to retrieve some info..."  ) %(ip) , 0 ,show_percent=False)
        gtk.gdk.threads_leave()
        
        
        info_percent=0.0
        info_items=0
        for key, value in self.main.config.vars:
            if self.main.config.GetVar(key) == 1:
                info_items +=1
        if info_items != 0:
            percent_step=float((100/info_items))
            percent_step=percent_step/100
        
        
        
        if self.main.config.GetVar("tcosinfo") == 1:
            info_percent+=percent_step
            self.update_progressbar( info_percent )
        
            if tcos_vars["get_client"] == "tcos":
                self.datatxt.insert_block( _("Tcos info") , image=shared.IMG_DIR + "tcos-icon-32x32.png" )
        
            elif tcos_vars["get_client"] == "pxes":
                self.datatxt.insert_block( _("PXES info") , image="/usr/share/pixmaps/pxesconfig/2X.png" )
        
            elif tcos_vars["get_client"] == "ltsp":
                self.datatxt.insert_block( _("LTSP info") , image=shared.IMG_DIR + "ltsp_logo.png" )
        
            else:
                self.datatxt.insert_block( _("Unknow client info")  )
        
            tcos_vars["hostname"]=self.main.localdata.GetHostname(ip)
            tcos_vars["version"]=self.main.xmlrpc.GetVersion()

            #print_debug("tcos version: %s" %(tcos_vars["version"]) )

            if not tcos_vars["version"]:
                tcos_vars["version"]=_("unknow")
        
            self.datatxt.insert_list( [ 
            [ _("Hostname: "), tcos_vars["hostname"] ] , \
            [ _("Ip address: "), ip  ] , \
            [ _("TcosXmlRpc version: "), tcos_vars["version"] ]
            ] )
        
            tcos_vars["tcos_version"]=self.main.xmlrpc.ReadInfo("tcos_version")
            tcos_vars["tcos_generation_date"]=self.main.xmlrpc.ReadInfo("tcos_generation_date")
            tcos_vars["tcos_date"]=self.main.xmlrpc.ReadInfo("tcos_date")
            
            self.datatxt.insert_list( [ \
            [_("Tcos image version: "), tcos_vars["tcos_version"] ], \
            [_("Tcos image date: "), tcos_vars["tcos_generation_date"] ], \
            [_("Date of thin client: "), tcos_vars["tcos_date"] ]
             ] )
        
        
            
        if self.main.config.GetVar("kernelmodulesinfo") == 1:
            info_percent+=percent_step
            self.update_progressbar( info_percent )
            
            self.datatxt.insert_block( _("Kernel info"),  image=shared.IMG_DIR + "info_kernel.png" )
            
            tcos_vars["kernel_version"]=self.main.xmlrpc.ReadInfo("kernel_version")
            tcos_vars["kernel_complete_version"]=self.main.xmlrpc.ReadInfo("kernel_complete_version")
            tcos_vars["modules_loaded"]=self.main.xmlrpc.ReadInfo("modules_loaded")
            tcos_vars["modules_notfound"]=self.main.xmlrpc.ReadInfo("modules_notfound")
            
            if tcos_vars["modules_notfound"] != "OK":
                
                blabel=_("Force download and mount all modules")
                self.main.action_button=gtk.Button( label=blabel )
                self.main.action_button.connect("clicked", self.on_downloadallmodules_click)
                self.main.action_button.show()
                
                tcos_vars["modules_notfound"] = """
                <span style='color:red'>%s </span>
                <input type='button' name='%s' label='%s' />
                """ %(tcos_vars["modules_notfound"], "self.main.action_button" , blabel)
                
            else:
                tcos_vars["modules_notfound"] = _("None")
            
            self.datatxt.insert_list( [ \
            [_("Kernel version: "), tcos_vars["kernel_version"] ], \
            [_("Kernel complete version: "), tcos_vars["kernel_complete_version"] ], \
            [_("Loaded Modules: "), tcos_vars["modules_loaded"] ], \
            [_("Modules not found: "), tcos_vars["modules_notfound"] ] 
             ] )
             
        
        cpuinfo=self.main.config.GetVar("cpuinfo")
        pciinfo=self.main.config.GetVar("pcibusinfo")
        ramswapinfo=self.main.config.GetVar("ramswapinfo")
        networkinfo=self.main.config.GetVar("networkinfo")
        
        
        if cpuinfo == 1:
            info_percent+=percent_step
            self.update_progressbar( info_percent )
        
            self.datatxt.insert_block( _("Cpu info: "), image=shared.IMG_DIR + "info_cpu.png"  ) 
            
            tcos_vars["cpu_model"]=self.main.xmlrpc.ReadInfo("cpu_model")
            tcos_vars["cpu_vendor"]=self.main.xmlrpc.ReadInfo("cpu_vendor")
            tcos_vars["cpu_speed"]=self.main.xmlrpc.ReadInfo("cpu_speed")
            
            self.datatxt.insert_list( [ \
            [_("Cpu model: "), tcos_vars["cpu_model"] ], \
            [_("Cpu vendor: "), tcos_vars["cpu_vendor"] ], \
            [_("Cpu speed: "), tcos_vars["cpu_speed"] ] 
             ] )
             
        
        if pciinfo == 1:
            info_percent+=percent_step
            self.update_progressbar( info_percent )
        
            # PCI info
            self.datatxt.insert_block( _("PCI buses: ") , image=shared.IMG_DIR + "info_pci.png" )
            
            pcilist=[]
            allpci=self.main.xmlrpc.tc.tcos.pci("pci_all").replace('\n', '').split(' ')
            for pci_id in allpci:
                if pci_id != "":
                    pci_info=self.main.xmlrpc.tc.tcos.pci(pci_id).replace('\n', '')
                    pcilist.append( [pci_id + " ", pci_info] )
            
            self.datatxt.insert_list( pcilist )
        
        
        
        if self.main.config.GetVar("processinfo") == 1:
            info_percent+=percent_step
            self.update_progressbar( info_percent )
            
            self.datatxt.insert_block( _("Process running: "), image=shared.IMG_DIR + "info_proc.png"  )
            
            proclist=[]
            allprocess=self.main.xmlrpc.ReadInfo("get_process").replace('\n', '').split('|')
            self.datatxt.insert_proc( allprocess )
            
        
        if ramswapinfo == 1:
            info_percent+=percent_step
            self.update_progressbar( info_percent )
            
            self.datatxt.insert_block( _("Ram info: "), image=shared.IMG_DIR + "info_ram.png"  )
            
            tcos_vars["ram_total"]=self.main.xmlrpc.ReadInfo("ram_total")
            tcos_vars["ram_free"]=self.main.xmlrpc.ReadInfo("ram_free")
            tcos_vars["ram_active"]=self.main.xmlrpc.ReadInfo("ram_active")
            
            self.datatxt.insert_list( [ \
            [_("Total Ram: "), tcos_vars["ram_total"] ], \
            [_("Free RAM: "), tcos_vars["ram_free"] ], \
            [_("Active RAM: "), tcos_vars["ram_active"] ] 
             ] )
            
            self.datatxt.insert_block( _("Swap info: ") ,image=shared.IMG_DIR + "info_swap.png" )
            tcos_vars["swap_avalaible"]=self.main.xmlrpc.ReadInfo("swap_avalaible")
            tcos_vars["swap_total"]=self.main.xmlrpc.ReadInfo("swap_total")
            tcos_vars["swap_used"]=self.main.xmlrpc.ReadInfo("swap_used")
            
            self.datatxt.insert_list( [ \
            [_("Swap enabled: "), tcos_vars["swap_avalaible"] ], \
            [_("Total Swap: "), tcos_vars["swap_total"] ], \
            [_("Used Swap: "), tcos_vars["swap_used"] ] 
             ] )
            
            
        
        if networkinfo == 1:
            info_percent+=percent_step
            self.update_progressbar( info_percent )
        
            self.datatxt.insert_block( _("Network info: ") , image=shared.IMG_DIR + "info_net.png" )
            
            tcos_vars["network_hostname"]=self.main.xmlrpc.ReadInfo("network_hostname")
            tcos_vars["network_ip"]=self.main.xmlrpc.ReadInfo("network_ip")
            tcos_vars["network_mask"]=self.main.xmlrpc.ReadInfo("network_mask")
            tcos_vars["network_mac"]=self.main.xmlrpc.ReadInfo("network_mac")
            tcos_vars["network_rx"]=self.main.xmlrpc.ReadInfo("network_rx")
            tcos_vars["network_tx"]=self.main.xmlrpc.ReadInfo("network_tx")
            
            self.datatxt.insert_list( [ \
            [_("Network hostname: "), tcos_vars["network_hostname"] ], \
            [_("Network IP: "), tcos_vars["network_ip"] ], \
            [_("Network MASK: "), tcos_vars["network_mask"] ], \
            [_("Network MAC: "), tcos_vars["network_mac"] ], \
            [_("Data received(rx): "), tcos_vars["network_rx"] ], \
            [_("Data send(tx): "), tcos_vars["network_tx"] ] 
             ] )
            
            
        if self.main.config.GetVar("xorginfo") == 1:
            info_percent+=percent_step
            self.update_progressbar( info_percent )
        
            self.datatxt.insert_block( _("Xorg info") , image=shared.IMG_DIR + "info_xorg.png" )
        
            xorglist=[]
            
            alldata=self.main.xmlrpc.tc.tcos.xorg("get", "", \
                 self.main.config.GetVar("xmlrpc_username"), \
                 self.main.config.GetVar("xmlrpc_password")  ).replace('\n', '').split()
            print_debug ( "populate_datatxt() %s" %( " ".join(alldata) ) )
            if alldata[0].find("error") == 0:
                shared.error_msg( _("Error getting Xorg info:\n%s" ) %( " ".join(alldata)  )
            else:
                for data in alldata:
                    try:
                        (key,value)=data.split('=')
                    except:
                        key=data
                        value=""
                
                    if value== "1":
                        value = _("enabled")
                    elif value == "0":
                        value = _("disabled")
                    
                    if key == "xsession":
                        key=_("X Session Type")
                    elif key == "xdriver":
                        key=_("Xorg Driver")
                    elif key == "xres":
                        key=_("Xorg Resolution")
                    elif key == "xdepth":
                        key=_("Xorg Color depth")
                    elif key =="xdpms":
                        key=_("DPMS energy monitor control")
                    elif key == "xdontzap":
                        key=_("Disable kill X with Ctrl+Alt+Backspace")
                    elif key == "xmousewheel":
                        key=_("Enable mouse wheel")
                    elif key == "xrefresh":
                        key=_("Refresh rate")
                    elif key == "xfontserver":
                        key = _("Xorg font server")
                    elif key == "xmousedev":
                        key = _("Mouse device")
                    elif key == "xmouseprotocol":
                        key = _("Mouse protocol")
                    elif key == "xhorizsync":
                        key = _("X Horiz sync")
                    elif key == "xvertsync":
                        key = _("X Vert sync")
                    xorglist.append( [key + " " , value] )
            self.datatxt.insert_list(xorglist)
            
            
        if self.main.config.GetVar("soundserverinfo") == 1:
            info_percent+=percent_step
            self.update_progressbar( info_percent )
        
            # make a ping to port
            from ping import PingPort
            if PingPort(ip, shared.pulseaudio_soundserver_port, 0.5).get_status() == "OPEN":
                self.datatxt.insert_block ( _("PulseAudio Sound server is running"), image=shared.IMG_DIR + "info_sound_ok.png" )
                
                channel_list=[]
                tcos_sound_vars={}
                tcos_sound_vars["allchannels"]=self.main.xmlrpc.GetSoundChannels()
                print_debug ( "populate_datatxt() sound channels=%s" %(tcos_sound_vars["allchannels"]) )
                
                counter=0
                self.main.volume_sliders=[]
                self.main.volume_checkboxes=[]
                
                self.datatxt.insert_html("""
                <br />
                <div style='text-align:center; background-color:#f3d160 ; margin-left: 25%%; margin-right: 25%%'>
                    <img file="%s" />
                    <span style='font-weight: bold; font-size: 150%%'>%s</span>
                </div>
                """ %( shared.IMG_DIR + "icon_mixer.png", _("Remote Sound Mixer")) )
                
                
                for channel in tcos_sound_vars["allchannels"]:
                    volumebutton=None
                    # only show channel in list
                    if not channel in shared.sound_only_channels:
                        #print "not show channel=%s" %(channel)
                        continue
                    txt="""
                    <div style='text-align:center; background-color:#f3d160 ; margin-left: 25%%; margin-right: 25%%'>
                    <span style='font-size: 120%%'>%s: </span>
                    """ %(channel)
                    #tcos_sound_vars[channel+"_level"]=self.main.xmlrpc.GetSoundInfo(channel, mode="--getlevel")
                    #tcos_sound_vars[channel+"_mute"]=self.main.xmlrpc.GetSoundInfo(channel, mode="--getmute")
                    
                    
                    value=self.main.xmlrpc.GetSoundInfo(channel, mode="--getlevel")
                    value=value.replace('%','')
                    try:
                        value=float(value)
                    except:
                        value=0.0
                    
                    ismute=self.main.xmlrpc.GetSoundInfo(channel, mode="--getmute")
                    if ismute == "off":
                        ismute = True
                    else:
                        ismute = False
                    
                    print_debug ( "populate_datatxt() channel=%s ismute=%s volume level=%s" %(channel, ismute, value) )
                    ############ mute checkbox ##################
                    volume_checkbox=gtk.CheckButton(label=_("Mute"), use_underline=True)
                    volume_checkbox.set_active(ismute)
                    volume_checkbox.connect("toggled", self.checkbox_value_changed, channel, ip)
                    volume_checkbox.show()
                    self.main.volume_checkboxes.append(volume_checkbox)
                    
                    txt+="<input type='checkbox' name='self.main.volume_checkboxes' index='%s' />" %(counter)
                    
                    
                    ############# volume slider ###################
                    adjustment = gtk.Adjustment(value=0,
                                         lower=0,
                                         upper=100,
                                         step_incr=1,
                                         page_incr=1);
                    volume_slider = gtk.HScale(adjustment)
                    volume_slider.set_size_request(100, 30)
                    volume_slider.set_value_pos(gtk.POS_RIGHT)
                        
                    volume_slider.set_value( value )
                    volume_slider.connect("button_release_event", self.slider_value_changed, adjustment, channel, ip)
                    volume_slider.connect("scroll_event", self.slider_value_changed, adjustment, channel, ip)
                    volume_slider.show()
                    self.main.volume_sliders.append(volume_slider)
                    txt+="<input type='slider' name='self.main.volume_sliders' index='%s' />" %(counter)
                    
                    txt+="</div>"
                    self.datatxt.insert_html(txt)
                    counter+=1
                
                # PulseAudio utils
                self.main.openvolumecontrol_button=None
                self.main.openvolumecontrol_button=gtk.Button(label=_("PulseAudio Control") )
                self.main.openvolumecontrol_button.connect("clicked", self.on_openvolumecontrol_button_click, ip)
                self.main.openvolumecontrol_button.show()
                
                self.main.openvolumemeter_button=None
                self.main.openvolumemeter_button=gtk.Button(label=_("PulseAudio Meter") )
                self.main.openvolumemeter_button.connect("clicked", self.on_openvolumemeter_button_click, ip)
                self.main.openvolumemeter_button.show()
                
                self.main.volumemanager_button=None
                self.main.volumemanager_button=gtk.Button(label=_("PulseAudio Manager") )
                self.main.volumemanager_button.connect("clicked", self.on_volumemanager_button_click, ip)
                self.main.volumemanager_button.show()
                
                self.datatxt.insert_block(_("PulseAudio utils: ") + """ 
                <input type='button' name='self.main.volumemanager_button' />
                <input type='button' name='self.main.openvolumecontrol_button' />
                <input type='button' name='self.main.openvolumemeter_button' />
                """)
                
                self.datatxt.insert_block( _("PulseAudio stats") )
                pulseaudioinfo=self.main.xmlrpc.GetSoundInfo(channel="", mode="--getserverinfo")
                pulseaudioinfo=pulseaudioinfo.replace('\n','').split('|')
                #print pulseaudioinfo
                allpulseaudioinfo=[]
                for line in pulseaudioinfo:
                    if line != "" and line.find(":") != -1:
                        key, value = line.split(':')
                        allpulseaudioinfo.append([ key+":", value ])
                self.datatxt.insert_list( allpulseaudioinfo )
                
            else:
                self.datatxt.insert_block ( "Sound server is not running", image=shared.IMG_DIR + "info_sound_ko.png")
        
        gtk.gdk.threads_enter()
        self.datatxt.display()
        self.update_progressbar( 1 )
        self.main.progressbar.hide()
        #self.main.write_into_statusbar( "" )
        gtk.gdk.threads_leave()
        
        crono(start1, "populate_datatxt(%s)" %(ip) )
        return False


    def slider_value_changed(self, widget, adjustment, event, channel, ip):
        value=widget.get_value()
        print_debug ( "slider_value_changed() ip=%s channel=%s value=%s" %(ip, channel, value) )
        
        self.main.write_into_statusbar( \
        _("Changing value of %(channel)s channel, to %(value)s%%..." )\
         %{"channel":channel, "value":value} )
        
        newvalue=self.main.xmlrpc.SetSound(ip, channel, str(value)+"%") 
        
        self.main.write_into_statusbar( \
        _("Changed value of %(channel)s channel, to %(value)s" ) \
        %{"channel":channel, "value":newvalue} )
    
    def checkbox_value_changed(self, widget, channel, ip):
        value=widget.get_active()
        if not value:
            value="off"
            self.main.write_into_statusbar( _("Unmuting %s channel..."  ) %(channel) )
            newvalue=self.main.xmlrpc.SetSound(ip, channel, value="", mode="--setunmute")   
        else:
            value="on"
            self.main.write_into_statusbar( _("Muting %s channel..."  ) %(channel) )
            newvalue=self.main.xmlrpc.SetSound(ip, channel, value="", mode="--setmute")
        self.main.write_into_statusbar( _("Status of %(channel)s channel, is \"%(newvalue)s\""  )\
         %{"channel":channel, "newvalue":newvalue} )
        #self.main.write_into_statusbar( _("Changed mute status of %s channel, to %s" %(channel, newvalue) ) )
        
    def populate_hostlist(self, clients):
        print_debug ( "populate_hostlist() init" )
        start1=time()
        
        
        
        # clean list
        print_debug ( "populate_hostlist() clear list and start progressbar!!!" )
        
        gtk.gdk.threads_enter()
        #disable refresh button
        self.main.refreshbutton.set_sensitive(False)
        self.main.progressbar.show()
        self.main.progressbutton.show()
        self.set_progressbar( _("Searching info of hosts..."), 0)
        self.model.clear()
        gtk.gdk.threads_leave()
        
        inactive_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'inactive.png')
        active_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'active.png')
        
        logged_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'logged.png')
        unlogged_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'unlogged.png')
        
        locked_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'locked.png')
        unlocked_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'unlocked.png')
        
        i=0
        for host in clients:
            start2=time()
            if self.main.worker.is_stoped():
                print_debug ( "populate_hostlist() WORKER IS STOPPED" )
                break
            i += 1
            gtk.gdk.threads_enter()
            self.main.progressbar.show()
            self.set_progressbar( _("Connecting to %s...") \
                            %(host), float(i)/float(len(clients)) )
            gtk.gdk.threads_leave()
            
            
            self.main.localdata.newhost(host)
            self.main.xmlrpc.newhost (host)
            
            ip=host
            hostname=self.main.localdata.GetHostname(ip)
            username=self.main.localdata.GetUsername(ip)
            num_process=self.main.localdata.GetNumProcess(ip)
            time_logged=self.main.localdata.GetTimeLogged(ip)
            
            if self.main.localdata.IsActive(ip):
                image_active=active_image
            else:
                image_active=inactive_image
            
            if self.main.localdata.IsLogged(ip):
                image_logged=logged_image
            else:
                image_logged=unlogged_image
            
            if self.main.localdata.IsBlocked(host):
                image_blocked=locked_image
            else:
                image_blocked=unlocked_image
                
            gtk.gdk.threads_enter()
            self.iter = self.model.append (None)
            self.model.set_value (self.iter, COL_HOST, hostname )
            self.model.set_value (self.iter, COL_IP, host )
            self.model.set_value (self.iter, COL_USERNAME, username )
            self.model.set_value (self.iter, COL_ACTIVE, image_active )
            self.model.set_value (self.iter, COL_LOGGED, image_logged)
            self.model.set_value (self.iter, COL_BLOCKED, image_blocked)
            self.model.set_value (self.iter, COL_PROCESS, num_process )
            self.model.set_value (self.iter, COL_TIME, time_logged)
            gtk.gdk.threads_leave()
            
            crono(start2, "populate_host_list(%s)" %(ip) )
        
        gtk.gdk.threads_enter()
        self.main.progressbar.hide()
        self.main.progressbutton.hide()
        self.main.refreshbutton.set_sensitive(True)
        self.main.progressbutton.set_sensitive(True)
        gtk.gdk.threads_leave()
        
        self.main.worker.set_finished()
        crono(start1, "populate_host_list(ALL)" )
        return
    
    def menu_event_one(self, action):
        start1=time()
        (model, iter) = self.main.tabla.get_selection().get_selected()
        if iter == None:
            print_debug( "menu_event_one() not selected thin client !!!" )
            return
        self.main.selected_host=model.get_value(iter,0)
        self.main.selected_ip=model.get_value(iter, 1)
        if action == 0:
            # refresh terminal
            # call to read remote info
            self.main.xmlrpc.newhost(self.main.selected_ip)
            self.main.xmlrpc.ip=self.main.selected_ip
            
            self.main.worker=shared.Workers( self.main,\
                     target=self.populate_datatxt, args=([self.main.selected_ip]) ).start()
            
            
        if action == 1:
            # clean datatxtbuffer
            self.main.datatxt.clean()
            
        if action == 2:
            # Ask for reboot reboot
            ip=self.main.selected_ip
            msg=_( _("Do you want to reboot %s?" ) %(self.main.selected_ip) )
            if shared.ask_msg ( msg ):
                self.main.xmlrpc.Exe("reboot")
            
        if action == 3:
            # Ask for poweroff reboot
            msg=_( _("Do you want to poweroff %s?" ) %(self.main.selected_ip) )
            if shared.ask_msg ( msg ):
                self.main.xmlrpc.Exe("poweroff")    
        
        if action == 4:
            # lock screen
            if not self.main.xmlrpc.lockscreen():
                shared.error_msg( _("Can't connect to tcosxmlrpc.\nPlease verify user and password in prefences!") )
                return
            self.change_lockscreen(self.main.selected_ip)
        
        if action == 5:
            # unlock screen
            if not self.main.xmlrpc.unlockscreen():
                shared.error_msg( _("Can't connect to tcosxmlrpc.\nPlease verify user and password in prefences!") )
                return
            self.change_lockscreen(self.main.selected_ip)
        
        if action == 6:
            # start vnc
            self.main.worker=shared.Workers(self.main, target=self.start_ivs, args=([self.main.selected_ip]) )
            self.main.worker.start()
            
        if action == 7:
            # start vnc
            self.main.worker=shared.Workers(self.main, target=self.start_vnc, args=([self.main.selected_ip]) )
            self.main.worker.start()
            
        if action == 8:
            # screenshot !!!
            #Thread( target=self.get_screenshot, args=([self.main.selected_ip]) ).start()
            self.main.worker=shared.Workers(self.main, target=self.get_screenshot, args=[self.main.selected_ip])
            self.main.worker.start()
            #gobject.timeout_add( 50, self.get_screenshot, self.main.selected_ip )
            #self.get_screenshot(self.main.selected_ip)
        
        if action == 9:
            
            # give a remote xterm throught SSH
            pass_msg=_("Enter password of remote thin client (if asked for it)")
            cmd="xterm -e \"echo '%s'; ssh root@%s\"" %(pass_msg, self.main.selected_ip)
            print_debug ( "menu_event_one(%d) cmd=%s" %(action, cmd) )
            th=self.main.exe_cmd( cmd )
            
        if action == 10:
            # launch personalize settings if client is TCOS (PXES and LTSP not supported)
            client_type = self.main.xmlrpc.ReadInfo("get_client")
            if client_type == "tcos":
                cmd="gksu \"tcospersonalize --host=%s\"" %(self.main.selected_ip)
                print_debug ( "menu_event_one(%d) cmd=%s" %(action, cmd) )
                th=self.main.exe_cmd( cmd )
            else:
                shared.info_msg( _("%s is not supported to personalize!") %(client_type) )
            
        if action == 11:
            # reset xorg
            # Ask for it
            msg=_("Do you want to restart Xorg of %s?" ) %(self.main.selected_ip)
            if shared.ask_msg ( msg ):
                self.main.xmlrpc.Exe("restartx")
                self.refresh_client_info(self.main.selected_ip)
                
        if action == 12:
            # restart xorg with new settings
            # thin client must download again XXX.XXX.XXX.XXX.conf and rebuild xorg.conf
            msg=_( "Restart X session of %s with new config?" ) %(self.main.selected_ip)
            if shared.ask_msg ( msg ):
                #self.main.xmlrpc.login()
                # see xmlrpc/xorg.h, rebuild will download and sed xorg.conf.tpl
                self.main.xmlrpc.tc.tcos.xorg("rebuild", "--restartxorg", \
                    self.main.xmlrpc.username, \
                    self.main.xmlrpc.password  )
                # send killall Xorg && startx
                #self.main.xmlrpc.Exe("restartx")
                self.refresh_client_info(self.main.selected_ip)
        
        if action == 13:
            # exec app
            self.askfor(mode="exec", users=[self.main.localdata.GetUsername(self.main.selected_ip)])
            
        if action == 14:
            # exec app
            self.askfor(mode="mess", users=[self.main.localdata.GetUsername(self.main.selected_ip)] )
            
        if action == 15:
            print_debug ("menu_event_one() show running apps" )
            self.get_user_processes(self.main.selected_ip)
            
        crono(start1, "menu_event_one(%d)=\"%s\"" %(action, shared.onehost_menuitems[action] ) )
        return


    def start_vnc(self, ip):
        self.main.xmlrpc.newhost(ip)
        # check if remote proc is running
        if not self.main.xmlrpc.GetStatus("x11vnc"):
            gtk.gdk.threads_enter()
            self.main.write_into_statusbar( "Connecting with %s to start VNC support" %(ip) )
            gtk.gdk.threads_leave()
            
            try:
                self.main.xmlrpc.newhost(ip)
                self.main.xmlrpc.Exe("startvnc")
                gtk.gdk.threads_enter()
                self.main.write_into_statusbar( "Waiting for start of VNC server..." )
                gtk.gdk.threads_leave()
                sleep(5)
            except:
                gtk.gdk.threads_enter()
                shared.error_msg ( _("Can't start VNC, please add X11VNC support") )
                gtk.gdk.threads_leave()
                return
                
        cmd = "vncviewer " + ip
        print_debug ( "start_process() threading \"%s\"" %(cmd) )
        self.main.exe_cmd (cmd)
        
        gtk.gdk.threads_enter()
        self.main.write_into_statusbar( "" )
        gtk.gdk.threads_leave()

    def start_ivs(self, ip):
        self.main.xmlrpc.newhost(ip)
        # check if remote proc is running
        if not self.main.xmlrpc.GetStatus("ivs"):
            gtk.gdk.threads_enter()
            self.main.write_into_statusbar( "Connecting with %s to start iTALC support" %(ip) )
            gtk.gdk.threads_leave()
            
            try:
                self.main.xmlrpc.newhost(ip)
                if start_cmd == "":
                    start_cmd=remote_proc
                self.main.xmlrpc.Exe("startivs")
                gtk.gdk.threads_enter()
                self.main.write_into_statusbar( "Waiting for start of IVS server..." )
                gtk.gdk.threads_leave()
                sleep(5)
            except:
                gtk.gdk.threads_enter()
                shared.error_msg ( _("Can't start IVS, please add iTALC support") )
                gtk.gdk.threads_leave()
                return
                
        cmd = "icv " + ip + " root"
        print_debug ( "start_process() threading \"%s\"" %(cmd) )
        self.main.exe_cmd (cmd)
        
        gtk.gdk.threads_enter()
        self.main.write_into_statusbar( "" )
        gtk.gdk.threads_leave()

        
    def menu_event_all(self, action):
        start1=time()
        allclients=self.main.localdata.allclients
        allclients_txt=""
        for client in allclients:
            allclients_txt+="\n %s" %(client)
        #print self.main.localdata.allclients
        if len(self.main.localdata.allclients) == 0:
            shared.info_msg ( _("No clients connected, press refresh button.") )
            return
            
        if action == 0:
            # Ask for reboot
            msg=_( _("Do you want to reboot the following hosts:%s?" ) \
                                            %(allclients_txt) )
            if shared.ask_msg ( msg ):
                #gobject.timeout_add( 50, self.action_for_clients, allclients, "reboot" )
                self.main.worker=shared.Workers(self.main, None, None)
                self.main.worker.set_for_all_action(self.action_for_clients,\
                                                     allclients, "reboot" )
            return
        if action == 1:
            # Ask for poweroff
            msg=_( _("Do you want to poweroff the following hosts:%s?" )\
                                              %(allclients_txt) )
            if shared.ask_msg ( msg ):
                #gobject.timeout_add( 50, self.action_for_clients, allclients, "poweroff" )
                self.main.worker=shared.Workers(self.main, None, None)
                self.main.worker.set_for_all_action(self.action_for_clients,\
                                                     allclients, "poweroff" )
            return
        if action == 2:
            # Ask for lock screens
            msg=_( _("Do you want to lock the following screens:%s?" )\
                                                 %(allclients_txt) )
            if shared.ask_msg ( msg ):
                #gobject.timeout_add( 50, self.action_for_clients, allclients, "lockscreen" )
                self.main.worker=shared.Workers(self.main, None, None)
                self.main.worker.set_for_all_action(self.action_for_clients,\
                                                     allclients, "lockscreen" )
            return
        
        if action == 3:
            # Ask for unlock screens
            msg=_( _("Do you want to unlock the following screens:%s?" )\
                                                     %(allclients_txt) )
            if shared.ask_msg ( msg ):
                #gobject.timeout_add( 50, self.action_for_clients, allclients, "unlockscreen" )
                self.main.worker=shared.Workers(self.main, None, None)
                self.main.worker.set_for_all_action(self.action_for_clients,\
                                                    allclients, "unlockscreen" )
            return    
        
        if action == 4:
            shared.info_msg ( "FIXME" )
            print "LOGOUT FIXME"
            """
            # Ask for unlock screens
            msg=_( _("Do you want to unlock the following screens:%s?" ) %(allclients_txt) )
            if shared.ask_msg ( msg ):
                self.main.worker=shared.Workers(self.main, None, None)
                self.main.worker.set_for_all_action(self.main.xmlrpc.action_for_clients, allclients, "unlockscreen" )
            return
            """
        
        if action == 5:
            # Ask for restart X session
            msg=_( _("Do you want to restart X screens:%s?" )\
                                             %(allclients_txt) )
            if shared.ask_msg ( msg ):
                #gobject.timeout_add( 50, self.action_for_clients, allclients, "restartx" )
                self.main.worker=shared.Workers(self.main, None, None)
                self.main.worker.set_for_all_action(self.action_for_clients,\
                                                     allclients, "restartx" )
            return
        
        if action == 6:
            connected_users=[]
            for client in allclients:
                if self.main.localdata.IsLogged(client):
                    connected_users.append(self.main.localdata.GetUsername(client))
            self.askfor(mode="exec", users=connected_users)
        
        if action == 7:
            connected_users=[]
            for client in allclients:
                if self.main.localdata.IsLogged(client):
                    connected_users.append(self.main.localdata.GetUsername(client))
            self.askfor(mode="mess", users=connected_users)
        
        if action == 8:
            # demo mode
            # search for connected users
            connected_users=[]
            for client in allclients:
                if self.main.localdata.IsLogged(client):
                    connected_users.append(self.main.localdata.GetUsername(client))
            # start x11vnc in local 
            self.main.exe_cmd("x11vnc -shared -noshm -viewonly -forever -allow 127.0.0.1")
            
            # need to wait for start, PingPort loop
            from ping import PingPort
            status = "CLOSED"
            while status != "OPEN":
                status=PingPort("127.0.0.1",5900).get_status()
                if status == "CLOSED":
                    sleep(1)
            # exec this app
            remote_cmd="vncviewer 127.0.0.1 -ViewOnly -FullScreen"
            result = self.main.dbus_action.do_exec( connected_users , remote_cmd )
            if not result:
                shared.error_msg ( _("Error while exec remote app:\nReason: %s") %( self.main.dbus_action.get_error_msg() ) )
            self.main.write_into_statusbar( _("Running in demo mode.") )
        
        if action == 9:
            connected_users=[]
            for client in allclients:
                if self.main.localdata.IsLogged(client):
                    connected_users.append(self.main.localdata.GetUsername(client))
            result = self.main.dbus_action.do_killall( connected_users , "vncviewer" )
            
            # kill my x11vnc server
            self.main.exe_cmd("killall x11vnc")
            self.main.write_into_statusbar( _("Demo mode off.") )
        
        crono(start1, "menu_event[%d]=\"%s\"" %(action, shared.allhost_menuitems[action] ) )


    def action_for_clients(self, allhost, action):
        gtk.gdk.threads_enter()
        self.main.progressbar.show()
        #self.main.progressbutton.show()
        gtk.gdk.threads_leave()
        
        for ip in allhost:
            percent=float( allhost.index(ip)/len(allhost) )
            
            print_debug ( "doing %s in %s, percent complete=%f"\
                             %(action, ip, percent) )
            
            mydict={}
            mydict["action"]=action
            mydict["ip"]=ip
            gtk.gdk.threads_enter()
            self.set_progressbar( _("Doing action \"%(action)s\" in %(ip)s...") %mydict , percent )
            gtk.gdk.threads_leave()
        
            self.main.xmlrpc.newhost(ip)
            #self.main.xmlrpc.login()
            try:
                if action == "unlockscreen":
                    self.main.xmlrpc.unlockscreen()
                    # update icon
                    gtk.gdk.threads_enter()
                    self.change_lockscreen(ip)
                    gtk.gdk.threads_leave()
                elif action == "lockscreen":
                    self.main.xmlrpc.lockscreen()
                    # update icon
                    gtk.gdk.threads_enter()
                    self.change_lockscreen(ip)
                    gtk.gdk.threads_leave()
                else:
                    self.main.xmlrpc.Exe(action)
            except:
                print_debug ( "action_for_clients() error while exec %s in %s"\
                                         %(action, ip) )
                pass
        
            gtk.gdk.threads_enter()
            self.set_progressbar( _("Done action \"%(action)s\" in %(ip)s") %mydict , 1 )
            gtk.gdk.threads_leave()
            # wait (shared.wait_between_many_host) seconds per host to show progressbar???
            sleep(shared.wait_between_many_host)
        
        gtk.gdk.threads_enter()
        self.main.progressbar.hide()
        #self.main.progressbutton.hide()
        gtk.gdk.threads_leave()     
        return
        
        
    def change_lockscreen(self, ip):
        """
        change lockscreen icon
           status=True   icon=locked.png
           status=False  icon=unlocked.png
        """
        status=self.main.xmlrpc.status_lockscreen()
        print_debug ( "change_lockscreen(%s)=%s" %(ip, status) )
        if status:
            image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'locked.png')
        else:
            image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'unlocked.png')
        
        model=self.main.tabla.get_model()
        notvalid=[]
        model.foreach(self.lockscreen_changer, [ip, image])
        
        
    def lockscreen_changer(self, model, path, iter, args):
        ip, image = args
        # change image if ip is the same.
        if model.get_value(iter, 1) == ip:
            model.set_value(iter, 5, image)
    
    
    def get_screenshot(self, ip):
        # PingPort class put timeout very low to have more speed
        # get_screenshot need more time
        #import socket
        #socket.setdefaulttimeout(shared.socket_default_timeout)
        
        print_debug ("get_screenshot() INIT")
        # make screenshot
        print_debug ( "get_screenshot() scrot_size=%s" %(self.main.config.GetVar("scrot_size")) )
        
        # write into statusbar   
        #gtk.gdk.threads_enter()
        self.main.write_into_statusbar ( _("Trying to order terminal to do a screenshot...") )
        #gtk.gdk.threads_leave()
        
        if not self.main.xmlrpc.screenshot( self.main.config.GetVar("scrot_size") ):
            gtk.gdk.threads_enter()
            self.main.write_into_statusbar( _("Can't make screenshot, connection error") )
            gtk.gdk.threads_leave()
            return False
        
        print_debug ( "get_screenshot() creating button..." )
        
        slabel=_("Get another screenshot")
        self.main.another_screenshot_button=None
        self.main.another_screenshot_button=gtk.Button(label=slabel )
        self.main.another_screenshot_button.connect("clicked", self.on_another_screenshot_button_click, ip)
        self.main.another_screenshot_button.show()
        
            
        
        print_debug ( "get_screenshot() creating button..." )
        year, month, day, hour, minute, seconds ,wdy, yday, isdst= localtime()
        datetxt="%02d/%02d/%4d %02d:%02d:%02d" %(day, month, year, hour, minute, seconds)
        print_debug ( "get_screenshot() date=%s" %(datetxt) )
        
        
        block_txt=_("Screenshot of <span style='font-style: italic'>%s</span>")%(self.main.localdata.GetHostname(ip))
        block_txt+="<span style='font-size: medium'> %s </span>" %(datetxt)
        block_txt+="<span> </span><input type='button' name='self.main.another_screenshot_button' label='%s' />" %( slabel )
         
        url="http://%s:%s/capture-thumb.png" %(ip, shared.httpd_port)
        self.main.datatxt.clean()
        self.main.datatxt.insert_block( block_txt )
                                 
        self.main.datatxt.insert_html( "<img src='%s' alt='%s'/>\n"\
                                 %(url, _("Screenshot of %s" %(ip) )) )
        
        
        gtk.gdk.threads_enter()
        self.main.datatxt.display()
        self.main.write_into_statusbar ( _("Screenshot of %s, done.") %(ip)  )
        gtk.gdk.threads_leave()
        
        return False

    def update_hostlist(self):
        if self.main.config.GetVar("populate_list_at_startup") == "1":
            if float(self.main.config.GetVar("refresh_interval")) > 0:
                update_every=float(self.main.config.GetVar("refresh_interval"))
                print_debug ( "update_hostlist() every %f secs" %(update_every) )
                gobject.timeout_add(int(update_every * 1000), self.main.populate_host_list )
                return
        
    def get_user_processes(self, ip):
        """get user processes in session"""
        print_debug( "get_user_processes(%s) __init__" %ip )
        #check user is connected
        if not self.main.localdata.IsLogged(ip):
            print_debug ("get_user_processes(%s) NOT LOGGED" %ip)
            shared.info_msg( _("User not connected, no processes.") )
            return
        username=self.main.localdata.GetUsername(ip)
        cmd="LANG=C ps U \"%s\" -o pid,command" %(username)
        print_debug ( "get_user_processes(%s) cmd=%s " %(ip, cmd) )
        process=self.main.localdata.exe_cmd(cmd, verbose=0)
        
        
        self.main.datatxt.clean()
        self.main.datatxt.insert_block(   _("Running processes for user \"%s\": " ) %(username), image=shared.IMG_DIR + "info_proc.png"  )
        
        if self.main.config.GetVar("systemprocess") == "0":
            self.main.datatxt.insert_block ( \
            _("ALERT: There are some system process hidden. Enable it in Preferences dialog.") \
            , image=shared.IMG_DIR + "icon_alert.png" ,\
            color="#f08196", size="medium" )
        
        self.main.datatxt.insert_html ( """
        <br/><div style='margin-left: 135px; margin-right: 200px;background-color:#ead196;color:blue'>""" + _("Pid") + "\t" 
        + "\t" + _("Process command") +"</div>" )
        
        #self.main.datatxt.insert_html("<div>")
        
        counter=0
        self.main.kill_proc_buttons=None
        self.main.kill_proc_buttons=[]
        blabel=_("Kill this process")
        
        for proc in process:
            is_hidden=False
            if proc.split()[0]== "PID":
                continue
            pid=proc.split()[0] # not convert to int DBUS need string
            name=" ".join(proc.split()[1:])
            name=name.replace('<','&lt;').replace('>','&gt;')
            
            if int(self.main.config.GetVar("systemprocess")) == 0:
                for hidden in shared.system_process:
                    if hidden in name:
                        #print_debug ( "get_user_processes() hidden process, not show \"%s\"" %(name) )
                        is_hidden=True
            
            if is_hidden:
                continue
            
            
            kill_button=gtk.Button(label=blabel)
            kill_button.connect("clicked", self.on_kill_button_click, pid, username)
            kill_button.show()
            self.main.kill_proc_buttons.append(kill_button)
                    
            self.main.datatxt.insert_html("""
            <span style='background-color: red; margin-left: 5px; margin-right: 0px'>
            <input type='button' name='self.main.kill_proc_buttons' index='%d' label='%s' /></span>
            <span style='color: red; margin-left: 140px; margin-right: 0px'> %6s</span>
            <span style='color: blue; margin-left: 350px; margin-right: 0px'> %s</span><br />
            """ %(counter, blabel, pid, name) ) 
            counter+=1
        
        #print counter    
        #self.main.datatxt.insert_html("</div>")
        self.main.datatxt.display()
        return
    
    def refresh_client_info(self, ip):
        print_debug ( "refresh_client_info() updating host data..." )
        model=self.main.tabla.get_model()
        model.foreach(self.refresh_client_info2, [ip] )
    
    def refresh_client_info2(self, model, path, iter, args):
        ip = args[0]
        print_debug ( "refresh_client_info2()  ip=%s model_ip=%s" %(ip, model.get_value(iter, 1)) )
        #print ip
        #print model.get_value(iter, 1)
        # update data if ip is the same.
        if model.get_value(iter, 1) == ip:
            #sleep(2)
            self.set_client_data(ip, model, iter)
            
            
    def set_client_data(self, ip, model, iter):
        print_debug ( "refresh_client_info2() updating host data..." )
        
        inactive_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'inactive.png')
        active_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'active.png')
        
        logged_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'logged.png')
        unlogged_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'unlogged.png')
        
        locked_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'locked.png')
        unlocked_image = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + 'unlocked.png')
        
        # disable cache
        self.main.localdata.cache_timeout=0
           
        if self.main.localdata.IsActive(ip):
            image_active=active_image
        else:
            image_active=inactive_image
            
        if self.main.localdata.IsLogged(ip):
            image_logged=logged_image
        else:
            image_logged=unlogged_image
            
        if self.main.localdata.IsBlocked(ip):
            image_blocked=locked_image
        else:
            image_blocked=unlocked_image
        
        
        hostname=self.main.localdata.GetHostname(ip)
        username=self.main.localdata.GetUsername(ip)
        num_process=self.main.localdata.GetNumProcess(ip)
        time_logged=self.main.localdata.GetTimeLogged(ip)
        
        #enable cache again
        self.main.localdata.cache_timeout=shared.cache_timeout
            
        model.set_value (iter, COL_HOST, hostname )
        model.set_value (iter, COL_IP, ip )
        model.set_value (iter, COL_USERNAME, username )
        model.set_value (iter, COL_ACTIVE, image_active )
        model.set_value (iter, COL_LOGGED, image_logged)
        model.set_value (iter, COL_BLOCKED, image_blocked)
        model.set_value (iter, COL_PROCESS, num_process )
        model.set_value (iter, COL_TIME, time_logged)

    def RightClickMenuOne(self, path):
        """ menu for one client"""
        print_debug ( "RightClickMenuOne() creating menu" )
        self.main.menu=gtk.Menu()
        
        #menu header
        if path == None:        
            menu_items = gtk.MenuItem(_("Actions for selected host"))
            self.main.menu.append(menu_items)
            menu_items.set_sensitive(False)
            menu_items.show()
        else:
            model=self.main.tabla.get_model()
            menu_items = gtk.MenuItem( _("Actions for %s") %(model[path][1]) )
            self.main.menu.append(menu_items)
            menu_items.set_sensitive(False)
            menu_items.show()
            
        #add all items in shared.onehost_menuitems
        
        for i in range( len(shared.onehost_menuitems) ):
            icon_file_found=False
            if shared.onehost_menuitems[i][1] != None:
                icon_file_found=True
                icon_file=shared.IMG_DIR +\
                          shared.onehost_menuitems[i][1]
                          
                if not os.path.isfile(icon_file):
                    icon_file_found=False
            
            if icon_file_found:
                # we have icon
                menu_items=gtk.ImageMenuItem(shared.onehost_menuitems[i][0], True)
                icon = gtk.Image()
                icon.set_from_file(icon_file)
                menu_items.set_image(icon)
            else:
                buf = shared.onehost_menuitems[i][0]
                menu_items = gtk.MenuItem(buf)
                
            self.main.menu.append(menu_items)
            menu_items.connect("activate", self.on_rightclickmenuone_click, i)
            menu_items.show()
            
    def RightClickMenuAll(self):
        """ menu for ALL clients"""
        self.main.allmenu=gtk.Menu()
        
        #menu headers
        menu_items = gtk.MenuItem(_("Actions for all hosts"))
        self.main.allmenu.append(menu_items)
        menu_items.set_sensitive(False)
        menu_items.show()
        
        for i in range(len(shared.allhost_menuitems)):
            icon_file_found=False
            if shared.allhost_menuitems[i][1] != None:
                icon_file_found=True
                icon_file=shared.IMG_DIR +\
                          shared.allhost_menuitems[i][1]
                          
                if not os.path.isfile(icon_file):
                    icon_file_found=False
            
            if icon_file_found:
                # we have icon
                menu_items=gtk.ImageMenuItem(shared.allhost_menuitems[i][0], True)
                icon = gtk.Image()
                icon.set_from_file(icon_file)
                menu_items.set_image(icon)
            else:
                buf = shared.allhost_menuitems[i][0]
                menu_items = gtk.MenuItem(buf)
                
            self.main.allmenu.append(menu_items)
            menu_items.connect("activate", self.on_rightclickmenuall_click, i)
            menu_items.show()
        
        
        
    def on_hostlist_event(self, widget, event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = self.main.tabla.get_path_at_pos(x, y)
            if pthinfo is not None:
                
                path, col, cellx, celly = pthinfo
                #generate menu
                self.RightClickMenuOne( path )
                
                self.main.tabla.grab_focus()
                self.main.tabla.set_cursor( path, col, 0)
                self.main.menu.popup( None, None, None, event.button, time)
                return 1
            else:
                self.main.allmenu.popup( None, None, None, event.button, time)
                print_debug ( "on_hostlist_event() NO row selected" )
                return
            

if __name__ == "__main__":
    app=TcosActions(None)
