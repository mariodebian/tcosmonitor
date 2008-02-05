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
website_label=_("TcosMonitor web page")


# default debug value (overwrite with --debug or -d)
debug=False

# default TCOS config file (default in this path, if installed use global)
tcos_config_file="./tcos.conf"

# if exec from svn or sources dir
if os.path.isdir('./debian') and os.path.isdir('./po') and os.path.isdir('extensions'):
    LOCALE_DIR = "./po/"
    GLADE_DIR = "./"
    IMG_DIR = "./images/"
    EXTENSIONS="./extensions"
    tcos_config_file="./tcos.conf"
    print "exec in sources dir"
else:
    tcos_config_file="/etc/tcos/tcos.conf"
    GLADE_DIR = "/usr/share/tcosmonitor/"
    IMG_DIR = "/usr/share/tcosmonitor/images/"
    LOCALE_DIR = "/usr/share/locale"
    EXTENSIONS="/usr/share/tcosmonitor/extensions/"


# config file
config_file=os.path.expanduser('~/.tcosmonitor.conf')

scan_methods=[
"netstat", 
"ping",
"static"
]


DefaultConfig=[
["populate_list_at_startup", 0, "int"],
["work_as_cyber_mode", 0, "int"],
["refresh_interval", 10, "int"],
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
["tcosmonitorversion", version, "str"],
["blockactioninthishost", 1, "int"],
["onlyshowtcos", 1, "int"],
["selectedhosts", 0, "int"],
["statichosts", "", "str"],
["ssh_remote_username", "root", "str"],
["vlc_audio_codec", "mp3", "str"]
]
# method ping is list 0 of combo_scan_method


# gettext support
setlocale( LC_ALL )
bindtextdomain( PACKAGE, LOCALE_DIR )
textdomain( PACKAGE )

# text file enabling or disabling tcos-devices-ng or tcos-volume-manager
module_conf_file="/etc/tcos/tcosmonitor.conf"

httpd_port=8081

xmlremote_port=8080
xmlremote_url="/RPC2"

pulseaudio_soundserver_port=4713
sound_only_channels=["Master", "PCM", "Line", "CD", "Mic", "Aux", "vol", "pcm", "line", "cd", "mic"]

hidden_network_ifaces=["lo", "sit0", "wmaster0", "vmnet0", "vmnet1", "vbox0", "vbox1", "vbox2"]

cache_timeout=20

wait_between_many_host=0.1
socket_default_timeout=15

dbus_disabled=False

disable_textview_on_update=True


NO_LOGIN_MSG="----"

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

###
###   [ TEXT, ICON (in images dir) ]
###
onehost_menuitems=[
 [ _("Refresh terminal info"), "menu_refresh.png"] ,          #action=0
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
 ]


allhost_menuitems=[
 [ _("Reboot all clients"), "menu_reboot.png"] ,                  #action=0
 [ _("Poweroff all clients"), "menu_poweroff.png"] ,              #action=1
 [ _("Lock all screens"), "menu_lock.png" ] ,                     #action=2
 [ _("Unlock all screens"), "menu_unlock.png" ] ,                 #action=3
 [ _("Logout clients"), "menu_restartx.png" ] ,   # FIXME need an icon           #action=4
 [ _("Restart X session of all clients"),  "menu_newconf.png" ] ,#action=5
 [ _("Exec same app in all connected users") , "menu_exec.png" ] ,#action=6
 [ _("Send a text message to all connected users") , "menu_msg.png" ], #action=7
 [ _("Enter demo mode, all connected users see my screen") , "menu_tiza.png" ], #action=8
 [ _("Capture All clients screens") , "menu_screenshot.png" ],    #action=9
 [ _("Audio/Video broadcast") , "menu_broadcast.png" ],                 #action=10
 [ _("Send files") , "menu_send.png" ]                          #action=11
 ]


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
 "bash"
]



# TcosPersonalize stuff

remotehost=None

xsession_values=[
"XDMCP",  
"local", 
"sshX",
"FreeNX"
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
        print "%s::%s" %(__name__, txt)
    return


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
        mydict={}
        print_debug( _("QUESTION: %(txt)s, RESPONSE %(response)s")  %{"txt":txt, "response":response} )
        return response

    def info_msg(txt):
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
            if line == '\n': continue
            if line.find('#') == 0: continue
            line=line.replace('\n', '')
            if "=" in line:
                if line.split('=')[0] == module:
                    if line.split('=')[1] == "0":
                        return False
                    else:
                        return True


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
        try:
            self.main.progressbutton.set_sensitive(True)
        except:
            pass
        
        if self.main.worker_running == False:
            self.th.start()     # start thread
            self.set_started()  # config var as started
            self.start_watch_dog(self.th) # start watch_dog
        else:
            print_debug ( "worker() other work pending... not starting" )
        
    def stop(self):
        self.__stop=True
        self.__finished=True
        #self.main.worker_running=False
        
    def set_finished(self):
        self.__finished = True
        self.__stop=False
        self.main.worker_running=False

    def set_started(self):
        self.__finished=False
        self.__stop=False
        self.main.worker_running=True

    def is_stoped(self):
        return self.__stop
        
    def get_finished(self):
        return self.__finished

    def set_for_all_action(self, function, allhost, action):
        action_args=[allhost, action]
        Thread( target=function, args=(action_args) ).start()


