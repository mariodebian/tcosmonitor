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
from time import time
import gtk
import os

from tcosmonitor import shared
from tcosmonitor.TcosExtensions import TcosExtension
from tcosmonitor.ping import PingPort

def crono(start, txt):
    print_debug ("crono(), %s get %f seconds" %(txt, (time() - start)) )
    return

def print_debug(txt):
    if shared.debug:
        print "%s::%s" % ("extensions::info", txt)
    return


class Info(TcosExtension):
    def register(self):
        self.main.menus.register_simple(_("Refresh terminal info"), "menu_refresh.png", 0, self.get_info, "info")
        # register file click event target
        self.main.listview.populate_datatxt=self.populate_datatxt

    def get_info(self, widget, ip):
        if not self.get_client():
            return
        print_debug("get_info() ip=%s"%(ip))
        self.main.xmlrpc.ip=ip
        self.main.worker=shared.Workers( self.main,\
                     target=self.populate_datatxt, args=(ip,) ).start()
    

    def populate_datatxt(self, ip):
        start1=time()
        print_debug ("populate_datatxt() INIT ip %s"%ip)
        
        if not self.main.xmlrpc.connected:
            print_debug ( "populate_datatxt(%s) NO CONNECTION" %(ip) )
            crono(start1, "populate_datatxt(%s)" %(ip) )
            return
        
        # dictionary with all data
        tcos_vars={}
        
        self.datatxt = self.main.datatxt
        
        # clear datatxt
        self.main.common.threads_enter("TcosActions:populate_datatxt clean datatxt")
        self.datatxt.clean()
        self.main.common.threads_leave("TcosActions:populate_datatxt clean datatxt")
        tcos_vars["get_client"] = self.main.xmlrpc.ReadInfo("get_client")
        print_debug ( "Client type=%s" %(tcos_vars["get_client"]) )
        
        # print into statusbar
        self.main.common.threads_enter("TcosActions:populate_datatxt show progressbar")
        
        if shared.disable_textview_on_update and self.main.listview.isactive():
            self.main.tabla.set_sensitive(True)
        
        #self.main.write_into_statusbar( _("Connecting with %s to retrieve some info..."  ) %(ip) )
        
        self.main.progressbar.show()
        #self.main.progressbutton.show()
        self.main.actions.set_progressbar( _("Connecting with %s to retrieve some info..."  ) %(ip) , 0, show_percent=False)
        
        self.main.common.threads_leave("TcosActions:populate_datatxt show progressbar")
        
        
        info_percent=0.0
        info_items=0
        for elem in self.main.config.vars:
            # elem can have 2 or 3 elements (don't use key,value in for)
            key=elem[0]
            value=elem[1]
            if self.main.config.GetVar(key) == 1:
                info_items += 1
        if info_items != 0:
            percent_step=float((100/info_items))
            percent_step=percent_step/100
        
        
        
        if self.main.config.GetVar("tcosinfo") == 1:
            info_percent+=percent_step
            self.main.common.threads_enter("TcosActions:populate_datatxt update progressbar")
            self.main.actions.update_progressbar( info_percent )
            self.main.common.threads_leave("TcosActions:populate_datatxt update progressbar")
        
            if tcos_vars["get_client"] == "tcos":
                self.datatxt.insert_block( _("Tcos info") , image=shared.IMG_DIR + "tcos-icon-32x32.png" )
        
            elif tcos_vars["get_client"] == "pxes":
                self.datatxt.insert_block( _("PXES info") , image="/usr/share/pixmaps/pxesconfig/2X.png" )
        
            elif tcos_vars["get_client"] == "ltsp":
                self.datatxt.insert_block( _("LTSP info") , image=shared.IMG_DIR + "ltsp_logo.png" )
            
            elif tcos_vars["get_client"] == "standalone":
                self.datatxt.insert_block( _("Standalone info") , image=shared.IMG_DIR + "standalone.png" )
        
            else:
                self.datatxt.insert_block( _("Unknow client info")  )
        
            tcos_vars["hostname"]=self.main.localdata.GetHostname(ip)
            tcos_vars["version"]=self.main.xmlrpc.GetVersion()

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
            tcos_vars["tcos_uptime"]=self.main.xmlrpc.ReadInfo("tcos_uptime")
            
            self.datatxt.insert_list( [ \
            [_("Tcos image version: "), tcos_vars["tcos_version"] ], \
            [_("Tcos image date: "), tcos_vars["tcos_generation_date"] ], \
            [_("Date of thin client: "), tcos_vars["tcos_date"] ],
            [_("Uptime: "), tcos_vars["tcos_uptime"] ]
             ] )
        
        
            
        if self.main.config.GetVar("kernelmodulesinfo") == 1:
            info_percent+=percent_step
            self.main.common.threads_enter("TcosActions:populate_datatxt update progressbar")
            self.main.actions.update_progressbar( info_percent )
            self.main.common.threads_leave("TcosActions:populate_datatxt update progressbar")
            
            self.datatxt.insert_block( _("Kernel info"),  image=shared.IMG_DIR + "info_kernel.png" )
            
            tcos_vars["kernel_version"]=self.main.xmlrpc.ReadInfo("kernel_version")
            tcos_vars["kernel_complete_version"]=self.main.xmlrpc.ReadInfo("kernel_complete_version")
            tcos_vars["modules_loaded"]=self.main.xmlrpc.ReadInfo("modules_loaded")
            tcos_vars["modules_notfound"]=self.main.xmlrpc.ReadInfo("modules_notfound")
            
            if tcos_vars["modules_notfound"] != "OK" and tcos_vars["get_client"] == "tcos":
                
                blabel=_("Force download and mount all modules")
                self.main.action_button=gtk.Button( label=blabel )
                self.main.action_button.connect("clicked", self.on_downloadallmodules_click)
                self.main.action_button.show()
                
                tcos_vars["modules_notfound"] = """
                <span style='color:red'>%s </span>
                <input type='button' name='%s' label='%s' />
                """ % (tcos_vars["modules_notfound"], "self.main.action_button" , blabel)
                
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
            self.main.common.threads_enter("TcosActions:populate_datatxt update progressbar")
            self.main.actions.update_progressbar( info_percent )
            self.main.common.threads_leave("TcosActions:populate_datatxt update progressbar")
        
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
            self.main.common.threads_enter("TcosActions:populate_datatxt update progressbar")
            self.main.actions.update_progressbar( info_percent )
            self.main.common.threads_leave("TcosActions:populate_datatxt update progressbar")
        
            # PCI info
            self.datatxt.insert_block( _("PCI buses: ") , image=shared.IMG_DIR + "info_pci.png" )
            
            pcilist=[]
            try:
                allpci=self.main.xmlrpc.tc.tcos.pci("pci_all").split(' ')
            except Exception, err:
                print_debug("info() Exception pci error %s"%err)
                self.main.xmlrpc.CheckSSL(err)
                pass
            for pci_id in allpci:
                if pci_id != "":
                    try:
                        pci_info=self.main.xmlrpc.tc.tcos.pci(pci_id)
                        pcilist.append( [pci_id + " ", pci_info] )
                    except Exception, err:
                        print_debug("info() Exception pci error %s"%err)
                        self.main.xmlrpc.CheckSSL(err)
                        pass
            
            self.datatxt.insert_list( pcilist )
        
        
        
        if self.main.config.GetVar("processinfo") == 1 and tcos_vars["get_client"] != "standalone":
            info_percent+=percent_step
            self.main.common.threads_enter("TcosActions:populate_datatxt update progressbar")
            self.main.actions.update_progressbar( info_percent )
            self.main.common.threads_leave("TcosActions:populate_datatxt update progressbar")
            
            self.datatxt.insert_block( _("Process running: "), image=shared.IMG_DIR + "info_proc.png"  )
            
            proclist=[]
            allprocess=self.main.xmlrpc.ReadInfo("get_process").split('|')
            self.datatxt.insert_proc( allprocess )
            
        
        if ramswapinfo == 1:
            info_percent+=percent_step
            self.main.common.threads_enter("TcosActions:populate_datatxt update progressbar")
            self.main.actions.update_progressbar( info_percent )
            self.main.common.threads_leave("TcosActions:populate_datatxt update progressbar")
            
            self.datatxt.insert_block( _("Ram info: "), image=shared.IMG_DIR + "info_ram.png"  )
            
            tcos_vars["ram_total"]=self.main.xmlrpc.ReadInfo("ram_total")
            tcos_vars["ram_free"]=self.main.xmlrpc.ReadInfo("ram_free")
            tcos_vars["ram_active"]=self.main.xmlrpc.ReadInfo("ram_active")
            
            self.datatxt.insert_list( [ \
            [_("Total Ram: "), tcos_vars["ram_total"] ], \
            [_("Free RAM: "), tcos_vars["ram_free"] ], \
            [_("Active RAM: "), tcos_vars["ram_active"] ] 
             ] )
            
            self.datatxt.insert_block( _("Swap info: "), image=shared.IMG_DIR + "info_swap.png" )
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
            self.main.common.threads_enter("TcosActions:populate_datatxt update progressbar")
            self.main.actions.update_progressbar( info_percent )
            self.main.common.threads_leave("TcosActions:populate_datatxt update progressbar")
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
            
            
        if self.main.config.GetVar("xorginfo") == 1 and tcos_vars["get_client"] != "standalone":
            info_percent+=percent_step
            self.main.common.threads_enter("TcosActions:populate_datatxt update progressbar")
            self.main.actions.update_progressbar( info_percent )
            self.main.common.threads_leave("TcosActions:populate_datatxt update progressbar")
        
            self.datatxt.insert_block( _("Xorg info") , image=shared.IMG_DIR + "info_xorg.png" )
        
            xorglist=[]
            try:
                alldata=self.main.xmlrpc.tc.tcos.xorg("get", "", \
                    self.main.config.GetVar("xmlrpc_username"), \
                    self.main.config.GetVar("xmlrpc_password")  ).split()
            except Exception, err:
                print_debug("info() Exception networking error %s"%err)
                self.main.xmlrpc.CheckSSL(err)
                pass
                
            print_debug ( "populate_datatxt() %s" %( " ".join(alldata) ) )
            if alldata[0].find("error") == 0:
                #shared.error_msg( _("Error getting Xorg info:\n%s" ) %( " ".join(alldata)) )
                pass
            else:
                for data in alldata:
                    try:
                        (key, value)=data.split('=')
                    except Exception, err:
                        print_debug("populate_datatxt() Exception spliting data=%s, err=%s"%(data, err))
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
            self.main.common.threads_enter("TcosActions:populate_datatxt update progressbar")
            self.main.actions.update_progressbar( info_percent )
            self.main.common.threads_leave("TcosActions:populate_datatxt update progressbar")
        
            # make a ping to port
            if PingPort(ip, shared.pulseaudio_soundserver_port, 0.5).get_status() == "OPEN":
                self.datatxt.insert_block ( _("PulseAudio Sound server is running"), image=shared.IMG_DIR + "info_sound_ok.png" )
                
                channel_list=[]
                tcos_sound_vars={}
                #tcos_sound_vars["allchannels"]=self.main.xmlrpc.GetSoundChannels()
                tcos_sound_vars["allchannels"]=self.main.xmlrpc.GetSoundChannelsContents()
                #print_debug ( "populate_datatxt() sound channels=%s" %(tcos_sound_vars["allchannels"]) )
                
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
                    if not channel['name'] in shared.sound_only_channels:
                        print_debug("populate_datatxt() *** AUDIO CHANNEL HIDDEN*** channel=%s"%channel)
                        continue
                    txt="""
                    <div style='text-align:center; background-color:#f3d160 ; margin-left: 25%%; margin-right: 25%%'>
                    <span style='font-size: 120%%'>%s: </span>
                    """ %(channel['name'])
                    
                    
                    #value=self.main.xmlrpc.GetSoundInfo(channel, mode="--getlevel")
                    #value=value.replace('%','')
                    value=channel['level']
                    try:
                        value=float(value)
                    except Exception, err:
                        print_debug("populate_datatxt() Exception getting volume=%s, err=%s"%(value, err) )
                        value=0.0
                    
                    #ismute=self.main.xmlrpc.GetSoundInfo(channel, mode="--getmute")
                    ismute=channel['mute']
                    if ismute == "off":
                        ismute = True
                    else:
                        ismute = False
                    
                    ctype=channel['type']
                    print_debug ( "populate_datatxt() channel=%s ismute=%s volume level=%s ctype=%s" %(channel['name'], ismute, value, ctype) )
                    ############ mute checkbox ##################
                    volume_checkbox=gtk.CheckButton(label=_("Mute"), use_underline=True)
                    volume_checkbox.set_active(ismute)
                    volume_checkbox.connect("toggled", self.checkbox_value_changed, channel['name'], ip)
                    if "switch" in ctype:
                        volume_checkbox.show()
                    else:
                        volume_checkbox.hide()
                    self.main.volume_checkboxes.append(volume_checkbox)
                    
                    txt+="<input type='checkbox' name='self.main.volume_checkboxes' index='%s' />" %(counter)
                    
                    
                    ############# volume slider ###################
                    adjustment = gtk.Adjustment(value=0,
                                         lower=0,
                                         upper=100,
                                         step_incr=1,
                                         page_incr=1)
                    volume_slider = gtk.HScale(adjustment)
                    volume_slider.set_size_request(100, 30)
                    volume_slider.set_value_pos(gtk.POS_RIGHT)
                    volume_slider.set_digits(0)
                    volume_slider.set_value( value )
                    volume_slider.connect("button_release_event", self.slider_value_changed, adjustment, channel['name'], ip)
                    volume_slider.connect("scroll_event", self.slider_value_changed, adjustment, channel['name'], ip)
                    if "volume" in ctype:
                        volume_slider.show()
                    else:
                        volume_slider.hide()
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
                pulseaudioinfo=self.main.xmlrpc.GetSoundInfo(channel="", mode="--getserverinfo").split('|')
                #print pulseaudioinfo
                allpulseaudioinfo=[]
                allpulseaudioinfo_trans=[]
                output=[]
                for line in pulseaudioinfo:
                    if line != "" and line.find(":") != -1:
                        key, value = line.split(':')
                        allpulseaudioinfo.append([ key+":", value ]) 
                        allpulseaudioinfo_trans.append(value)
                if len(allpulseaudioinfo_trans) == 11:
                    output.append( ["%s:" %( _("Currently in use")), allpulseaudioinfo_trans[0] ])
                    output.append( ["%s:" %( _("Allocated during whole lifetime")), allpulseaudioinfo_trans[1] ])
                    output.append( ["%s:" %( _("Sample cache size")), allpulseaudioinfo_trans[2] ])
                    output.append( ["%s:" %( _("User name")), allpulseaudioinfo_trans[3] ])
                    output.append( ["%s:" %( _("Host Name")), allpulseaudioinfo_trans[4] ])
                    output.append( ["%s:" %( _("Server Name")), allpulseaudioinfo_trans[5] ])
                    output.append( ["%s:" %( _("Server Version")), allpulseaudioinfo_trans[6] ])
                    output.append( ["%s:" %( _("Default Sample Specification")), allpulseaudioinfo_trans[7] ])
                    output.append( ["%s:" %( _("Default Sink")), allpulseaudioinfo_trans[8] ])
                    output.append( ["%s:" %( _("Default Source")), allpulseaudioinfo_trans[9] ])
                    output.append( ["%s:" %( _("Cookie")), allpulseaudioinfo_trans[10] ])
                    self.datatxt.insert_list( output )
                else:
                    self.datatxt.insert_list( allpulseaudioinfo )
                
            else:
                self.datatxt.insert_block ( _("Sound server is not running"), image=shared.IMG_DIR + "info_sound_ko.png")
        
        self.main.common.threads_enter("TcosActions:populate_datatxt end")
        self.datatxt.display()
        self.main.actions.update_progressbar( 1 )
        self.main.progressbar.hide()
        
        if shared.disable_textview_on_update and self.main.iconview.isactive():
            self.main.tabla.set_sensitive(True)
        
        self.main.common.threads_leave("TcosActions:populate_datatxt end")
        
        crono(start1, "populate_datatxt(%s)" %(ip) )
        return False

    def on_downloadallmodules_click(self, widget):
        print_debug ( "on_downloadallmodules_click() ################" )
        if self.main.selected_ip != None:
            print_debug( "on_downloadallmodules_click() downloading modules for %s" %(self.main.selected_ip) )
            # download allmodules.squashfs and mount it
            self.main.xmlrpc.Exe("useallmodules.sh")
        return


    def slider_value_changed(self, widget, adjustment, event, channel, ip):
        value=widget.get_value()
        print_debug ( "slider_value_changed() ip=%s channel=%s value=%s" %(ip, channel, value) )
        
        self.main.write_into_statusbar( \
        _("Changing value of %(channel)s channel, to %(value)s%%..." )\
         %{"channel":channel, "value":value} )
        
        tmp=self.main.xmlrpc.SetSound(ip, channel, str(value)+"%")
        newvalue="%2d%%"%int(tmp['level'])
        
        self.main.write_into_statusbar( \
        _("Changed value of %(channel)s channel, to %(value)s" ) \
        %{"channel":channel, "value":newvalue} )
    
    def checkbox_value_changed(self, widget, channel, ip):
        value=widget.get_active()
        if not value:
            value="off"
            self.main.write_into_statusbar( _("Unmuting %s channel..."  ) %(channel) )
            tmp=self.main.xmlrpc.SetSound(ip, channel, value="", mode="--setunmute")
            newvalue=tmp['mute']
        else:
            value="on"
            self.main.write_into_statusbar( _("Muting %s channel..."  ) %(channel) )
            tmp=self.main.xmlrpc.SetSound(ip, channel, value="", mode="--setmute")
            newvalue=tmp['mute']
        self.main.write_into_statusbar( _("Status of %(channel)s channel, is \"%(newvalue)s\""  )\
         %{"channel":channel, "newvalue":newvalue} )


    def on_openvolumecontrol_button_click(self, widget, ip):
        print_debug ( "on_openvolumecontrol_button_click() ip=%s" %(ip) )
        cmd="PULSE_SERVER=\"%s\" pavucontrol" %(ip)
        if os.path.isdir("/dev/shm"):
            self.main.common.exe_cmd( cmd, verbose=0, background=True )
        else:
            shared.error_msg ( _("PulseAudio apps need /dev/shm.") )
        
    def on_openvolumemeter_button_click(self, widget, ip):
        print_debug ( "on_openvolumemeter_button_click()  ip=%s" %(ip) )
        cmd="PULSE_SERVER=\"%s\" pavumeter" %(ip)
        if os.path.isdir("/dev/shm"):
            self.main.common.exe_cmd( cmd, verbose=0, background=True )
        else:
            shared.error_msg ( _("PulseAudio apps need /dev/shm.") )
    
    def on_volumemanager_button_click(self, widget, ip):
        print_debug ( "on_volumemanager_button_click() ip=%s" %(ip) )
        cmd="PULSE_SERVER=\"%s\" paman" %(ip)
        if os.path.isdir("/dev/shm"):
            self.main.common.exe_cmd( cmd, verbose=0, background=True )
        else:
            shared.error_msg ( _("PulseAudio apps need /dev/shm.") )



__extclass__=Info








