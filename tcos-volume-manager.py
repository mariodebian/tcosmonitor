#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##########################################################################
# TcosMonitor writen by MarioDebian <mariodebian@gmail.com>
#
#    tcos-volume-manager version __VERSION__
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



import os, sys
import gobject
import getopt
from gettext import gettext as _

import pygtk
pygtk.require('2.0')
import gtk
from tcosmonitor import shared

# load conf file and exit if not active
if not shared.test_start("tcos-volume-manager") :
    print "tcos-volume-manager disabled at %s" % (shared.module_conf_file)
    sys.exit(1)


import pwd

def print_debug(txt):
    if shared.debug:
        print "%s::%s" % ("tcos-volume-manager", txt)

def get_username():
    return pwd.getpwuid(os.getuid())[0]


def usage():
    print "tcos-volume-manager help:"
    print ""
    print "   tcos-volume-manager [--host=XXX.XXX.XXX.XXX] "
    print "                 (force host to connect to change volumes, default is DISPLAY)"
    print "   tcos-volume-manager -d [--debug]  (write debug data to stdout)"
    print "   tcos-volume-manager -h [--help]   (this help)"


try:
    opts, args = getopt.getopt(sys.argv[1:], ":hd", ["help", "debug", "host="])
except getopt.error, msg:
    print msg
    print "for command line options use tcosconfig --help"
    sys.exit(2)

shared.remotehost, display =  os.environ["DISPLAY"].split(':')

# process options
for o, a in opts:
    if o in ("-d", "--debug"):
        print "DEBUG ACTIVE"
        shared.debug = True
    if o == "--host":
        #print "HOST %s" %(a)
        shared.remotehost = a
    if o in ("-h", "--help"):
        usage()
        sys.exit()

if shared.remotehost == "":
    print "tcos-volume-manager: Not allowed to run in local DISPLAY"
    #shared.error_msg ( _("tcos-volume-manager isn't allowed to run in local DISPLAY\nForce with --host=xx.xx.xx.xx") )
    sys.exit(0)



class TcosVolumeManager:
    def __init__(self, host):
        self.host=host
        self.name="TcosVolumeManager"
        self.visible=False
        
        if hasattr(gtk, 'status_icon_new_from_file'):
            # use gtk.status_icon
            icon = gtk.status_icon_new_from_file(shared.IMG_DIR + "tcos-volume-32x32.png")
            icon.set_tooltip( _("Tcos Sound levels on:\n%s") %(self.host) )
            icon.connect("activate", self.on_tray_icon_press_event)
        else:
            import egg.trayicon
            icon = egg.trayicon.TrayIcon("TCOS_sound")
            eventbox = gtk.EventBox()
            icon.add(eventbox)
            image=gtk.Image()
            image.set_from_file (shared.IMG_DIR + "tcos-volume-32x32.png")
            eventbox.add(image)
            tips = gtk.Tooltips()
            
            tips.set_tip(icon, ( _("Tcos Sound levels on:\n%s") %(self.host) )[0:79])
            tips.enable()
            icon.show_all()
            eventbox.connect("button_press_event", self.on_tray_icon_press_event)
        
        
        from tcosmonitor.ping import PingPort
        if PingPort(self.host, shared.xmlremote_port, 0.5).get_status() != "OPEN":
            shared.error_msg( _("ERROR: It appears that TcosXmlRpc is not running on %s.") %(self.host) )
            sys.exit(1)
            
        
        import tcosmonitor.TcosXauth
        self.xauth=tcosmonitor.TcosXauth.TcosXauth(self)
        self.xauth.init_standalone()
        
        # get all channels
        import tcosmonitor.TcosXmlRpc
        import tcosmonitor.TcosConf
        self.config=tcosmonitor.TcosConf.TcosConf(self, openfile=False)
        self.xmlrpc=tcosmonitor.TcosXmlRpc.TcosXmlRpc(self)
        
        nossl=True
        # make a test and exit if no cookie match
        if not self.xauth.test_auth(nossl):
            print "tcos-volume-manager: ERROR: Xauth cookie don't match"
            #sys.exit(1)
        
        self.xmlrpc.newhost(self.host,nossl)
        if not self.xmlrpc.connected:
            shared.error_msg( _("Error connecting with TcosXmlRpc in %s.") %(self.host) )
            sys.exit(1)
        
        self.allchannels=self.xmlrpc.GetSoundChannelsContents()
        print_debug ("__init__() %s" %( self.allchannels ) )
        
        import gettext
        gettext.bindtextdomain(shared.PACKAGE, shared.LOCALE_DIR)
        gettext.textdomain(shared.PACKAGE)
        
        # Widgets
        self.ui = gtk.Builder()
        self.ui.set_translation_domain(shared.PACKAGE)
        self.ui.add_from_file(shared.GLADE_DIR + 'tcos-volume-manager.glade')
        
        self.mainwindow = self.ui.get_object('mainwindow')
        
        # close windows signals
        #self.mainwindow.connect('destroy', self.quitapp )
        self.mainwindow.connect('delete-event', self.mainwindow_close )
        
        self.mainlabel=self.ui.get_object('mainlabel')
        
        self.scrolledwindow=self.ui.get_object('scrolledwindow')
        self.scrolledwindow2=self.ui.get_object('scrolledwindow2')
        
        self.quitbutton=self.ui.get_object('quitbutton')
        self.quitbutton.connect('clicked', self.quitapp )
        
        self.statusbar=self.ui.get_object('statusbar')
        self.refreshbutton=self.ui.get_object('refreshbutton')
        self.refreshbutton.connect('clicked', self.on_refresh_button )
        
        self.restartbutton=self.ui.get_object('restartbutton')
        self.restartbutton.connect('clicked', self.on_restart_button )
        
        # only show if we found this file in $HOME dir
        allowfile=os.path.expanduser("~/.tcos-volume-manager.allow.restartpulse")
        if os.path.isfile(allowfile):
            self.restartbutton.show()
        
        # restart on start
        restartfile=os.path.expanduser("~/.tcos-volume-manager.start.restartpulse")
        if os.path.isfile(restartfile):
            self.xmlrpc.RestartSoundDaemon()
        
        # FIXME try to not focus on quitbutton
        self.refreshbutton.grab_focus()
        
        self.get_channel_info()
        
    def on_refresh_button(self, widget):
        self.allchannels=self.xmlrpc.GetSoundChannelsContents()
        self.scrolledwindow.foreach( self.delete_child, self.scrolledwindow )
        self.scrolledwindow2.foreach( self.delete_child, self.scrolledwindow2 )
        self.get_channel_info()

    def on_restart_button(self, widget):
        self.xmlrpc.RestartSoundDaemon()
        self.on_refresh_button(None)

    def delete_child(self, widget, scrolled):
        scrolled.remove(widget)

    def get_channel_info(self):
        # retry cookie auth
        nossl=True
        self.xauth.test_auth(nossl)
        
        primary_channels=[]
        secondary_channels=[]
        if self.allchannels != None and len(self.allchannels) > 0:
            gobject.timeout_add( 50, self.write_into_statusbar, _("Loading channels info...") )
            for channel in self.allchannels:
                #if not channel in shared.sound_only_channels:
                if not channel['name'] in shared.sound_only_channels:
                    secondary_channels.append(channel)
                    continue
                primary_channels.append(channel)
            gobject.timeout_add( 500, self.populate_mixer, primary_channels, self.scrolledwindow)
            gobject.timeout_add( 1500, self.populate_mixer, secondary_channels, self.scrolledwindow2)
            #gobject.timeout_add( 4000, self.write_into_statusbar, _("Ready") )
            
        else:
            print_debug ( "ERROR: No auth" )
            gobject.timeout_add( 2000, self.write_into_statusbar, _("Error loading channels info (xauth error)") )
        
        self.mainwindow.set_icon_from_file(shared.IMG_DIR + 'tcos-icon-32x32.png')
        self.mainwindow.set_title( _("Tcos Volume Manager")  )
        self.mainlabel.set_markup( _("<b>Sound mixer of %s host</b>") %(self.host) )
        #self.mainwindow.show()
        
        #self.populate_mixer(primary_channels, self.scrolledwindow)
        #self.populate_mixer(secondary_channels, self.scrolledwindow2)
        
    
    def populate_mixer(self, all_channels, scrollwindow):
        box1 = gtk.HBox(False, 0)
        box1.set_border_width(0)
        box1.show()
        scrollwindow.add_with_viewport(box1)
        
        for channel in all_channels:
            #frame = gtk.Frame(channel)
            frame = gtk.Frame(channel['name'])
            #frame.show()
            box2 = gtk.VBox(False, 0)
            box2.set_border_width(0)
            
            ###########################################################
            #value=self.xmlrpc.GetSoundInfo(channel, mode="--getlevel")
            #value=value.replace('%','')
            value=channel['level']
            try:
                value=float(value)
            except Exception, err:
                print_debug("Exception, can't get float value, error=%s"%err)
                value=0.0
            ctype=channel['type']
            #ismute=self.xmlrpc.GetSoundInfo(channel, mode="--getmute")
            ismute=channel['mute']
            if ismute == "off":
                ismute = True
            else:
                ismute = False
            #print_debug ( "populate_mixer() channel=%s ismute=%s volume level=%s" %(channel, ismute, value) )
            print_debug ( "populate_mixer() channel=%s ismute=%s volume level=%s ctype=%s" %(channel['name'], ismute, value, ctype) )
            #############################################################
            adjustment = gtk.Adjustment(value=0,
                                         lower=0,
                                         upper=100,
                                         step_incr=1,
                                         page_incr=1)
            volume_slider = None
            volume_slider = gtk.VScale(adjustment)
            volume_slider.set_digits(0)
            volume_slider.set_inverted(True)
            
            volume_slider.set_size_request(30, 150)
            volume_slider.set_value_pos(gtk.POS_TOP)
            volume_slider.set_value( value )
            #volume_slider.connect("button_release_event", self.slider_value_changed, adjustment, channel, self.host)
            #volume_slider.connect("scroll_event", self.slider_value_changed, adjustment, channel, self.host)
            volume_slider.connect("button_release_event", self.slider_value_changed, adjustment, channel['name'], self.host)
            volume_slider.connect("scroll_event", self.slider_value_changed, adjustment, channel['name'], self.host)
            volume_slider.show()
            if "volume" in ctype:
                #volume_slider.show()
                volume_slider.set_sensitive(True)
            else:
                #volume_slider.hide()
                volume_slider.set_sensitive(False)
            
            box2.pack_start(volume_slider, False, True, 0)
            
            
            
            volume_checkbox=gtk.CheckButton(label=_("Mute"), use_underline=True)
            volume_checkbox.set_active(ismute)
            #volume_checkbox.set_size_request(30, 20)
            #volume_checkbox.connect("toggled", self.checkbox_value_changed, channel, self.host)
            volume_checkbox.connect("toggled", self.checkbox_value_changed, channel['name'], self.host)
            volume_checkbox.show()
            if "switch" in ctype:
                #volume_checkbox.show()
                volume_checkbox.set_sensitive(True)
            else:
                #volume_checkbox.hide()
                volume_checkbox.set_sensitive(False)
            
            
            box2.pack_start(volume_checkbox, False, True, 0)
            box2.show()
            frame.add(box2)
            
            frame.show()
            box1.pack_start(frame, True, True, 0)
        
        # write in statusbar if populating primary controls
        if scrollwindow == self.scrolledwindow:
            self.write_into_statusbar( _("Main controls ready") )
        
        # write in statusbar if populating secondary controls
        if scrollwindow == self.scrolledwindow2:
            self.write_into_statusbar( _("All remote controls loaded.") )
        return False
        

    def slider_value_changed(self, widget, event, adj, channel, ip):
        value=widget.get_value()
        print_debug ( "slider_value_changed() ip=%s channel=%s value=%s" %(ip, channel, value) )
        
        self.write_into_statusbar( \
        _("Changing value of %(channel)s channel, to %(value)s%%..." )\
         %{"channel":channel, "value":value} )
        
        tmp=self.xmlrpc.SetSound(ip, channel, str(value)+"%")
        newvalue="%2d%%"%int(tmp['level'])
        
        self.write_into_statusbar( \
        _("Changed value of %(channel)s channel, to %(value)s" ) \
        %{"channel":channel, "value":newvalue} )
    
    def checkbox_value_changed(self, widget, channel, ip):
        value=widget.get_active()
        if not value:
            value="off"
            self.write_into_statusbar( _("Unmuting %s channel..."  ) %(channel) )
            tmp=self.xmlrpc.SetSound(ip, channel, value="", mode="--setunmute")
            newvalue=tmp['mute']
        else:
            value="on"
            self.write_into_statusbar( _("Muting %s channel..."  ) %(channel) )
            tmp=self.xmlrpc.SetSound(ip, channel, value="", mode="--setmute")
            newvalue=tmp['mute']
        self.write_into_statusbar( _("Status of %(channel)s channel, is \"%(newvalue)s\""  )\
         %{"channel":channel, "newvalue":newvalue} ) 

    def write_into_statusbar(self, msg, *args):
        context_id=self.statusbar.get_context_id("status")
        self.statusbar.pop(context_id)
        self.statusbar.push(context_id, msg)
        return False

    def on_tray_icon_press_event(self, *args):
        if self.visible:
            self.mainwindow.hide()
        else:
            self.mainwindow.show()
        self.visible = not self.visible
        return
    
    def mainwindow_close(self, widget, event):
        print_debug ( "mainwindow_close() closing mainwindow to systray" )
        self.visible=False
        self.mainwindow.hide()
        return True

    def quitapp(self, *args):
        print_debug ( _("Exiting") )
        self.mainloop.quit()
        

    def run (self):
        self.mainloop = gobject.MainLoop()
        try:
            self.mainloop.run()
        except KeyboardInterrupt: # Ctrl+C Event
            self.quitapp()

if __name__ == "__main__":
    app=TcosVolumeManager(shared.remotehost)
    app.run()
