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

# Defaults values of TcosMonitor


import os
import sys
from gettext import gettext as _
from gettext import bindtextdomain, textdomain
from locale import setlocale, LC_ALL

have_display=False
allow_local_display=False

# import if DISPLAY is defined
if "DISPLAY" in os.environ:
    if os.environ["DISPLAY"] != "":
        have_display=True
        import pygtk
        pygtk.require('2.0')
        import gtk

# program name to use in gettext .mo
PACKAGE = "tcosmonitor"



# version
version="__VERSION__"
website="http://www.tcosproject.org"
LICENSE_FILE="/usr/share/common-licenses/GPL-2"

# default debug value (overwrite with --debug or -d)
debug=False

# default TCOS config file (default in this path, if installed use global)
tcos_config_file="./tcos.conf"

# if exec from svn or sources dir
if os.path.isdir('./debian') and os.path.isdir('./po'):
    LOCALE_DIR = "./po/"
    GLADE_DIR = "./ui/"
    IMG_DIR = "./images/"
    tcos_config_file="./tcos.conf"
    GLOBAL_CONF='./tcosmonitor.conf'
else:
    tcos_config_file="/etc/tcos/tcos.conf"
    GLADE_DIR = "/usr/share/tcosmonitor/ui/"
    IMG_DIR = "/usr/share/tcosmonitor/images/"
    LOCALE_DIR = "/usr/share/locale"
    GLOBAL_CONF='/etc/tcos/tcosmonitor.conf'


# gettext support
setlocale( LC_ALL )
bindtextdomain( PACKAGE, LOCALE_DIR )
textdomain( PACKAGE )

# config file
config_file=os.path.expanduser('~/.tcosmonitor.conf')
config_file_secrets=('/etc/tcos/secrets/tcosmonitor-secret')


scan_methods=[
"netstat", 
"ping",
"nmap"
"static"
]

vcodecs=["mp4v", "mp1v", "h264", "theo"]
vencs=["ffmpeg", "x264", "theora"]
acodecs=["mpga", "vorb"]
aencs=["ffmpeg", "vorbis"]
accesss=["udp", "http"]
muxs=["ts", "ogg"]

vlc_methods_send=[
"ffmpeg-MPEG4",
"ffmpeg-MPEG1",
"x264-MPEG4",
"http-Theora",
"http-MPEG1"
]

list_modes=[
['list', _("Traditional list only") ],
['icons', _("Icons only") ],
['class', _("Simulate classroom") ],
['both', _("Lists, icons and classroom with tabs") ],
    ]

DefaultConfig=[
["populate_list_at_startup", 0, "int"],
#["work_as_cyber_mode", 0, "int"],
["refresh_interval", 0, "int"],
["cache_timeout", 0, "int"],
["actions_timeout", 0, "int"],
["scan_network_method", "netstat", "str"],
["scrot_size", 65, "int"],      # % of screenshot
["miniscrot_size", 25, "int"],      # % of screenshot
["xmlrpc_username", "user", "str"], 
["xmlrpc_password","", "str"], 
["network_interface","eth0", "str"], 
["tcosinfo", 1, "int"], 
["cpuinfo", 0, "int"],
["kernelmodulesinfo", 0, "int"], 
["pcibusinfo", 0, "int"], 
["ramswapinfo", 0, "int"],
["processinfo", 0, "int"], 
["networkinfo", 0, "int"], 
["xorginfo", 0, "int"], 
["soundserverinfo", 0, "int"], 
["systemprocess", 0, "int"], 
["threadscontrol", 1, "int"], 
["tcosmonitorversion", version, "str"],
["blockactioninthishost", 1, "int"],
["notshowwhentcosmonitor", 0, "int"],
["onlyshowtcos", 1, "int"],
["selectedhosts", 0, "int"],
["statichosts", "", "str"],
["ssh_remote_username", "root", "str"],
["vlc_method_send", "ffmpeg-MPEG4", "str"],
["show_donate", 1, "int"],
["visible_menus", "", "str"],
["visible_buttons_menus", "", "str"],
["enable_sslxmlrpc", 0, "int"],
["ports_tnc", "", "str"],
["listmode", "list", "str"],
["menugroups", 1, "int"],
["positions", "", "str"],
["show_about", 1, "int"],
]

#
# IMPORTANT NOTE
# PLEASE DON'T SET "show__donate" TO "0" by default if you don't have a good reason
# tcosmonitor need to show this message when loads first time to get some
# users colaboration.
#
# Please contact with developers if you are not agree with this.
#


# method ping is list 0 of combo_scan_method



# text file enabling or disabling tcos-devices-ng or tcos-volume-manager
module_conf_file="/etc/tcos/tcosmonitor.conf"

httpd_port=8081

xmlremote_port=8998
xmlremote_sslport=8999
xmlremote_url="/RPC2"

pulseaudio_soundserver_port=4713
#
#char *dev_name[SOUND_MIXER_NRDEVICES] = { \
#        "Master", \
#        "Bass", \
#        "Treble", \
#        "Synth", \
#        "PCM", \
#        "Speaker", \
#        "Line", \
#        "Mic", \
#        "CD", \
#        "Mix", \
#        "PCM2", \
#        "Record", \
#        "Input", \
#        "Output", \
#        "Line 1", \
#        "Line 2", \
#        "Line 3", \
#        "Digital1", \
#        "Digital2", \
#        "Digital3", \
#        "Phone In", \
#        "PhoneOut", \
#        "Video", \
#        "Radio", \
#        "Monitor" };
#
sound_only_channels=["Front", "Master", "Master Front", "PCM", "Line", "CD", 
                    "Mic", "Front Mic", "Aux", "Headphone", "Speaker" , "PC Speaker", 
                    "vol", "pcm", "line", "cd", "mic",
                    "Mix", "PCM2", "Capture"]

hidden_network_ifaces=["lo", "sit0", "pan0", "wmaster0", "vmnet0", "vmnet1", "vmnet8", "vbox0", "vbox1", "vbox2", "vboxnet0", "vboxnet1"]

# for enable exclude users, change to "tcosmonitor-exclude"
dont_show_users_in_group="tcosmonitor-exclude"

check_tcosmonitor_user_group=False

tnc_only_ports="no"

cache_timeout=20

wait_between_many_host=0.1
socket_default_timeout=15

dbus_disabled=False

disable_textview_on_update=True

icon_image_thin="client.png"
icon_image_standalone="client.png"
icon_image_no_logged="host_tcos.png"


NO_LOGIN_MSG="---"

##
##  entry completion example apps
##

appslist=[
'xterm', 
'firefox', 
'iceweasel',
'gimp', 
'oowriter', 
'oocalc', 
'oodraw' ,
'gnumeric',
'abiword' ,
'gedit', 
'jclic', 
'amsn', 
'gftp',
'gcalctool',
'nautilus',
'konqueror',
'beep-media-player',
'audacious',
'tcos-volume-manager',
'tcos-devices-ng'
]

# main one host menus
###
###   [ TEXT, ICON (in images dir), [submenus index] ]
###
onehost_mainmenus = [
    [ _("Terminal actions") , "active.png", [0,2,3,4,5,22,23,9,10,12,19,1] ],
    [ _("User actions") , "logged.png", [11,13,14,15,20,21,6,7] ],
    [ _("Audio, video and files"), "multimedia.png", [8,17,16,18,24]],
]

###
###   [ TEXT, ICON (in images dir),     EXTENSION (or None) ]
###
onehost_menuitems=[
 [ _("Refresh terminal info"), "menu_refresh.png",  "extensions.info" , 0] ,          #action=0
 [ _("Clean info about terminal"), "menu_clear.png"] ,        #action=1
 [ _("Reboot"), "menu_reboot.png"] ,                          #action=2
 [ _("Poweroff"), "menu_poweroff.png"] ,                      #action=3
 [ _("Lock screen"), "menu_lock.png" ] ,                      #action=4
 [ _("Unlock screen"), "menu_unlock.png" ] ,                  #action=5
 [ _("Connect to remote screen (iTALC)"), "menu_remote.png" ],#action=6
 [ _("Connect to remote screen (VNC)"), "menu_remote.png" ] , #action=7
 [ _("Screenshot"), "menu_screenshot.png" ] ,                 #action=8
 [ _("Give a remote xterm"), "menu_xterm.png" ]  ,            #action=9
 [ _("Configure this host"), "menu_configure.png" ] ,         #action=10
 [ _("Logout client"),  "menu_restartx.png" ] ,               #action=11
 [ _("Restart X session with new settings"), "menu_newconf.png" ] , #action=12
 [ _("Exec app on user display") , "menu_exec.png" ] ,        #action=13
 [ _("Send a text message to user") , "menu_msg.png" ] ,      #action=14
 [ _("Show running apps of this client") , "menu_proc.png" ], #action=15
 [ _("Audio/Video broadcast") , "menu_broadcast.png" ],             #action=16
 [ _("Send files") , "menu_send.png" ],                       #action=17
 [ _("Demo mode (from this host)") , "menu_tiza.png" ],     #action=18
 [ _("Boot client (WakeOnLan)") , "menu_wol.png" ],                      #action=19
 [ _("Lock internet"), "menu_locknet.png" ] ,                 #action=20
 [ _("Unlock internet"), "menu_unlocknet.png" ],              #action=21
 [ _("DPMS Power off monitor"), "menu_dpms_off.png" ] ,     #action=22
 [ _("DPMS Power on monitor"), "menu_dpms_on.png" ],     #action=23
 [ _("Send MIC audio (from this host)"), "menu_rtp.png" ],     #action=24
 ]


# main one host menus
###
###   [ TEXT, ICON (in images dir), [submenus index] ]
###
allhost_mainmenus = [
    [ _("Terminal actions") , "active.png", [0,1,2,3,4,5,13,16,17] ],
    [ _("User actions") , "logged.png", [6,7,8,14,15,19] ],
    [ _("Audio, video and files"), "multimedia.png", [10,12,11,9,18]],
]

###
###   [ TEXT, ICON (in images dir) ]
###
allhost_menuitems=[
 [ _("Reboot all clients"), "menu_reboot.png"] ,                  #action=0
 [ _("Poweroff all clients"), "menu_poweroff.png"] ,              #action=1
 [ _("Lock all screens"), "menu_lock.png" ] ,                     #action=2
 [ _("Unlock all screens"), "menu_unlock.png" ] ,                 #action=3
 [ _("Logout clients"), "menu_restartx.png" ] ,                   #action=4
 [ _("Restart X session of all clients"),  "menu_newconf.png" ] ,#action=5
 [ _("Exec same app in all connected users") , "menu_exec.png" ] ,#action=6
 [ _("Send a text message to all connected users") , "menu_msg.png" ], #action=7
 [ _("Enter demo mode, all connected users see my screen") , "menu_tiza.png" ], #action=8
 [ _("Enter conference mode, all connected users can hear me") , "menu_rtp.png" ], #action=9
 [ _("Capture All clients screens") , "menu_screenshot.png" ],    #action=10
 [ _("Audio/Video broadcast") , "menu_broadcast.png" ],                 #action=11
 [ _("Send files") , "menu_send.png" ],                          #action=12
 [ _("Boot All clients (WakeOnLan)") , "menu_wol.png" ],                          #action=13
 [ _("Lock internet in all connected users"), "menu_locknet.png" ] ,                 #action=14
 [ _("Unlock internet in all connected users"), "menu_unlocknet.png" ],              #action=15
 [ _("DPMS Power off monitors"), "menu_dpms_off.png" ] ,     #action=16
 [ _("DPMS Power on monitors"), "menu_dpms_on.png" ],     #action=17
 [ _("Chat audio conference"), "menu_rtp.png" ],     #action=18
 [ _("Live view screens with VNC"), "menu_remote.png" ],     #action=19
 ]

preferences_menus_always_show={"menuone":[0,1], "menuall":[4]}

# format
#glade_widget,  [default_enabled,   menuone , menuall]
preferences_menus={
"ck_menu_lock":[        True,  [4,5],  [2,3] ],
"ck_menu_italc":[       False, [6],    [] ],
"ck_menu_vnc":[         True,  [7],    [] ],
"ck_menu_reboot":[      True,  [2,3],  [0,1] ],
"ck_menu_screenshots":[ True,  [8],    [10]],
"ck_menu_shell":[       False, [9],    []],
"ck_menu_xorg":[        True,  [10,11], [] ],
"ck_menu_restartx":[    True,  [12],   [5] ],
"ck_menu_exe":[         True,  [13],   [6] ],
"ck_menu_text":[        True,  [14],   [7] ],
"ck_menu_show":[        True,  [15],   [] ],
"ck_menu_video":[       True,  [16],   [11] ],
"ck_menu_send":[        True,  [17],   [12] ],
"ck_menu_demo":[        True,  [18],   [8] ],
"ck_menu_wakeonlan":[   False, [19],   [13] ],
"ck_menu_conference":[  True,  [24],     [9,18] ],
"ck_menu_net":[         True,  [20,21],[14,15] ],
"ck_menu_dpms":[        True,  [22,23],[16,17] ],
"ck_menu_personalize":[ False, [10],   [] ],
"ck_menu_livevnc":[    True,  [],     [19] ],
}

button_preferences_menus={
"ck_button_menu_chat":[               False ],
"ck_button_menu_list":[       False ],
"ck_button_menu_exe":[                False ],
"ck_button_menu_text":[               False ],
"ck_button_menu_video":[              False ],
"ck_button_menu_send":[               False ],
"ck_button_menu_audio":[         False ],
}


# this list contains all process to not show in user processes
system_process=[
 "dbus-daemon",
 "tcos-dbus-client", 
 "scp-client", 
 "ssh-agent", 
 "dbus-launch", 
 "gam_server", 
 "gconfd", 
 "gnome-keyring-daemon", 
 "gnome-applets", 
 "gnome-pty-helper", 
 "gnome-settings-daemon", 
 "-applet",
 "gnome-vfs",  
 "panel-plugins",
 "dcop", 
 "bonobo",
 "xauth",
 "faucet",
 "trackerd",
 "metacity",
 "gnome-panel",
 "nautilus",
 "gnome-power-manager",
 "gnome-cups-icon",
 "evolution-alarm-notify",
 "update-notifier",
 "system-config-printer",
 "gnome-volume-manager",
 "seahorse-agent",
 "smart-notifier",
 "[python]",
 "[sh]",
 "tcos-volume-manager",
 "notification-daemon",
 "bash",
 "gvfsd",
 "gconf-helper",
 "gdu-notification-daemon",
 "gvfs-gdu-volume",
 "gvfs-afc-volume-monitor",
 "gvfs-gphoto2-volume-monitor",
 "indicator-messages-service",
 "indicator-application-service",
 "indicator-sound-service",
 "notify-osd",
 "polkit-gnome-authentication-agent-1",
 "gvfs-fuse-daemon",
]



# TcosPersonalize stuff

remotehost=None

xsession_values=[
"XDMCP",  
"local", 
"sshX",
"FreeNX",
"rDesktop"
]
xsession_default="XDMCP"

# FIXME need to support other drivers
xdriver_values=[
"auto"
]
xdriver_default="auto"


# obtained from configure xorg
# grep "@" bin/configurexorg | \
#    grep Hz | awk -F ")" '{print $1}' | awk '{print $1", "}'
xres_values=[
"640x480 @ 60Hz",
"640x480 @ 72Hz",
"800x600 @ 60Hz",
"800x600 @ 72Hz",
"800x600 @ 85Hz",
"832x624 @ 75Hz",
"1024x768 @ 60Hz", # <= default
"1024x768 @ 70Hz",
"1024x768 @ 75Hz",
"1152x768 @ 54.8Hz",
"1152x864 @ 60Hz",
"1152x864 @ 75Hz",
"1280x768 @ 60Hz",
"1280x800 @ 60Hz",
"1280x960 @ 60Hz",
"1280x960 @ 85Hz",
"1280x1024 @ 60Hz",
"1400x1050 @ 60Hz",
"1400x1050 @ 75Hz",
"1440x900 @ 60Hz",
"1440x900 @ 75Hz",
"1600x1024 @ 85Hz",
"1600x1200 @ 60Hz",
"1600x1200 @ 75Hz",
"1600x1200 @ 85Hz",
"1680x1050 @ 60Hz",
"1792x1344 @ 75Hz",
"1792x1344 @ 60Hz",
"1856x1392 @ 60Hz",
"1856x1392 @ 75Hz",
"1920x1200 @ 60Hz",
"1920x1440 @ 60Hz",
"1920x1440 @ 75Hz",
"1920x1440 @ 85Hz",
"2048x1536 @ 60Hz",
"2048x1536 @ 75Hz",
"2048x1536 @ 85Hz",
]
xres_default="1024x768 @ 60Hz"


xdepth_values=[
"24", 
"16", 
"15", 
"8",
"4",  
"1"
]
xdepth_default="16"



PersonalizeConfig=[
["xdriver", xdriver_default, "str"],
["xres", xres_default, "str"],
["xdepth", xdepth_default, "str"], 
["xmousewheel",1, "int"], 
["xdontzap",0, "int"], 
["xdpms",1, "int"], 
["xsession", xsession_default, "str"], 
["xhorizsync", "", "str"], 
["xvertsync", "", "str"], 
["tcospersonalizeversion", version, "str"]
]



# shared functions

def print_debug(txt):
    if debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)


if have_display:
    def ask_msg(txt):
        response="yes"
        d = gtk.MessageDialog(None,
            gtk.DIALOG_MODAL |
            gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_YES_NO,
            txt)
        if d.run() == gtk.RESPONSE_YES:
            response=True
        else:
            response=False
        d.destroy()
        print_debug( _("QUESTION: %(txt)s, RESPONSE %(response)s")  %{"txt":txt, "response":response} )
        return response

    def info_msg(txt, urgency=False):
        if urgency:
            d = gtk.MessageDialog(None,
                          gtk.DIALOG_MODAL |
                          gtk.DIALOG_DESTROY_WITH_PARENT,
                          gtk.MESSAGE_INFO,
                          gtk.BUTTONS_OK_CANCEL,
                          None)
            d.set_markup(txt)
            if d.run() == gtk.RESPONSE_OK:
                response=True
            else:
                response=False
            d.destroy()
            print_debug ( _("INFO: %s") % txt )
            return response
        else:
            d = gtk.MessageDialog(None,
                          gtk.DIALOG_MODAL |
                          gtk.DIALOG_DESTROY_WITH_PARENT,
                          gtk.MESSAGE_INFO,
                          gtk.BUTTONS_OK,
                          txt)
            d.run()
            d.destroy()
        print_debug ( _("INFO: %s") % txt )

    def error_msg(txt):
        d = gtk.MessageDialog(None,
                      gtk.DIALOG_MODAL |
                      gtk.DIALOG_DESTROY_WITH_PARENT,
                      gtk.MESSAGE_WARNING,
                      gtk.BUTTONS_OK,
                      txt)
        d.run()
        d.destroy()
        print_debug ( _("ERROR: %s") % txt )


    def test_start(module):
        """
            read conf file and test if module is active
        """
        f=open(module_conf_file, "r")
        conf=f.readlines()
        f.close()
        
        for line in conf:
            if line == '\n':
                continue
            if line.find('#') == 0:
                continue
            line=line.replace('\n', '')
            if "=" in line:
                if line.split('=')[0] == module:
                    if line.split('=')[1] == "0":
                        return False
                    else:
                        return True

import binascii
import IPy
import ipaddr
import re


def is_bin(txt):
    if txt in ['3a', '2e', '61', '62', '63', '64', '65', '66']:
        # txt is ':' or '.' or a letter between a-f
        return False
    try:
        txt=int(txt)
    except ValueError:
        # can't convert txt to int, txt is hexadecimal aka binary
        return True
    
    if txt >= 30 and txt <= 39:
        # txt is between 0(0x30) and 9(0x39)
        return False
    # return binary by default
    return True

def parseIPAddress(ipstr, return_ipv4=True):
    """
    pass an string or binary IP and return IPV4
    """
    newip=[]
    isBin=False

    if ipstr.endswith(':0.0'):
        ipstr=ipstr.replace(':0.0', '')
    
    if ipstr.endswith(':0'):
        ipstr=ipstr.replace(':0', '')

    # hostname must start with letter and contain letters numbers and '-' or '.'
    if re.match(r'^[a-zA-Z][a-zA-Z0-9.-]+$', ipstr):
        # ipstr is a hostname
        return ipstr

    for it in ipstr:
        eol=is_bin(binascii.hexlify(it))
        if eol:
            isBin=True
        #print_debug("%s => %s string=%s"%(it, binascii.hexlify(it), eol) )
        newip.append(binascii.hexlify(it))
    
    if isBin:
        ip=ipaddr.IPAddress(IPy.parseAddress("0x" + "".join(newip) )[0])
    else:
        try:
            ip=ipaddr.IPAddress(ipstr)
        except Exception:
            #except Exception, err:
            #print_debug("parseIPAddress() Exception, error=%s"%err)
            return ipstr
    
    ipv4=ip
    if return_ipv4 and ip.version == 6 and ip.ipv4_mapped:
        ipv4=ip.ipv4_mapped.exploded
    
    return ipv4

if __name__ == "__main__":
    # test IPV6
    print "IPV6        '::ffff:10.0.2.22' => ", parseIPAddress('::ffff:10.0.2.22')

    # test binary IP
    import Xlib.xauth
    a=Xlib.xauth.Xauthority().entries[-1][1]
    print "Xlib        '%s' => " % a, parseIPAddress(a)

    # try with $DISPLAY
    print "DISPLAY     '192.168.0.10:0.0' => ", parseIPAddress('192.168.0.10:0.0')

    # try with hostname
    print "NAME        'tcos10:0.0' => ", parseIPAddress('tcos10:0.0')

    # try with Xephyr hostname
    print "XEPHYR NAME ':20.0' => ", parseIPAddress(':20.0')

from threading import Thread


class Workers:
    def __init__(self, main, target, args, dog=True):
        self.dog=dog
        self.main=main
        self.target=target
        self.args=args
        
        if not self.dog:
            #print_debug ( "worker() no other jobs job=%s args=%s" %(self.target, self.args) )
            self.th=Thread(target=self.target, args=(self.args) )
            self.__stop=True
            return
        
        if self.main.worker_running == True:
            #print_debug ( "worker() other jobs pending NO START job=%s args=%s" %(self.target, self.args) )
            pass
        else:
            #print_debug ( "worker() no other jobs job=%s args=%s" %(self.target, self.args) )
            self.th=Thread(target=self.target, args=(self.args) )
            self.__stop=True
    
    def start_watch_dog(self, dog_thread):
        if not self.dog:
            #print_debug ( "start_watch_dog() dog DISABLED" )
            return
        print_debug ( "start_watch_dog() starting watch dog..." )
        watch_dog=Thread(target=self.watch_dog, args=([dog_thread]) )
        watch_dog.start()

    def watch_dog(self, dog_thread):
        print_debug ( "watch_dog()  __init__ " )
        dog_thread.join()
        self.set_finished()
        print_debug ( "watch_dog() FINISHED" )
        
    def start(self):
        if hasattr(self.main, "progressbutton"):
            self.main.progressbutton.set_sensitive(True)
        
        if self.main.worker_running == False:
            self.set_started()  # config var as started
            self.th.start()     # start thread
            self.start_watch_dog(self.th) # start watch_dog
        else:
            print_debug ( "worker() other work pending... not starting" )
        
    def stop(self):
        self.__stop=True
        self.__finished=True
        #self.main.worker_running=False
        
    def set_finished(self):
        print_debug("worker set_finished() *****")
        self.__finished = True
        self.__stop=False
        self.main.worker_running=False

    def set_started(self):
        print_debug("worker set_started() *****")
        self.__finished=False
        self.__stop=False
        self.main.worker_running=True

    def is_stoped(self):
        return self.__stop
        
    def get_finished(self):
        return self.__finished

    def set_for_all_action(self, function, allhost, action):
        Thread( target=function, args=([allhost, action]) ).start()


