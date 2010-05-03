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

import gtk
import os
import sys
from gettext import gettext as _
from time import time

import gobject

import tcosmonitor.shared

def print_debug(txt):
    if tcosmonitor.shared.debug:
        print >> sys.stderr, "[%d] %s::%s" % (os.getpid(), __name__, txt)
        #print("[%d] %s::%s" % (os.getpid(), __name__, txt), file=sys.stderr)

def crono(start, txt):
    print_debug ("crono(), %s get %f seconds" %(txt, (time() - start)) )
    return


class TcosTrayIcon(object):
    def __init__(self, disable_quit=True, allow_reboot_poweroff=True):
        self.actions={}
        self.args={}
        self.first_time=True
        
        self.menu=gtk.Menu()
        if not disable_quit:
            self.items={ "quit": [_("Quit"), "menu_kill.png", True, None, None, False]  }
        else:
            self.items={}
        
        if allow_reboot_poweroff:
            self.items["reboot"]=[_("Reboot"), "menu_reboot.png", True, None, None, False]
            self.items["poweroff"]=[_("Poweroff"), "menu_poweroff.png", True, None, None, False]
        
        self.InitStatusIcon()
        self.InitMenu()
        

    def InitStatusIcon(self):
        self.statusIcon = gtk.status_icon_new_from_file(tcosmonitor.shared.IMG_DIR + "tcos-devices-32x32.png")
        self.statusIcon.set_tooltip( _("Tcos Devices") )

        # locale support
        import gettext
        gettext.bindtextdomain(tcosmonitor.shared.PACKAGE, tcosmonitor.shared.LOCALE_DIR)
        gettext.textdomain(tcosmonitor.shared.PACKAGE)

        self.ui = gtk.Builder()
        self.ui.set_translation_domain(tcosmonitor.shared.PACKAGE)
        self.ui.add_from_file(tcosmonitor.shared.GLADE_DIR + 'tray.ui')
        
        self.window = self.ui.get_object('popup')
        self.hide_button = self.ui.get_object("hide_button")

        self.hide_button.connect("clicked", self.close_popup)
        self.statusIcon.connect('popup-menu', self.popup_window)
        self.statusIcon.connect('activate', self.popup_window)
        
        self.devbox=self.ui.get_object("devbox")
        self.window = self.ui.get_object('popup')


    def InitMenu(self):
        #print_debug (" ##### InitMenu() ######")
        
        # clean devbox
        self.devbox=self.ui.get_object("devbox")
        self.devbox.foreach( lambda(widget): widget.destroy() )
        
        # sort items
        _sorted=self.items.keys()
        _sorted.sort()
        
        
        for m in _sorted:
            if m not in ["poweroff", "reboot", "quit"]:
                self.append_item(self.items[m], m)
        
        for extra in ["poweroff", "reboot", "quit"]:
            # add quit, reboot and poweroff menus at bottom
            if self.items.has_key(extra):
                self.append_item(self.items[extra], extra )

    def append_item(self, item, title):
        #print_debug("append_item() title=%s item=%s" %(title,item) )
        #return
        
        # need a table with 3 columns
        #
        #   ####################################
        #   #       #               #          #
        #   # Icon  #  Device info  #  Button  #
        #   #       #               #          #
        #   ####################################
        #
        table=gtk.Table(1, 3, False)
        table.set_col_spacings(5)
        
        status=self.items[title][5]
        #if title not in ['reboot', 'poweroff', 'quit']:
        #    print "          title %s status=%s"%(title, status)
        
         #######################################
        icon = gtk.Image()
        if item[1] != None: 
            icon_file_found=True
            icon_file=tcosmonitor.shared.IMG_DIR + item[1]
            if not os.path.isfile(icon_file):
                icon_file_found=False
        if title not in ['reboot', 'poweroff', 'quit'] and icon_file_found:
            # we have icon
            icon.set_from_file(icon_file)
            icon.set_sensitive(status)
        
        icon.show()
        #table.attach(icon, 0, 1, 0, 1, gtk.FILL, False, 0, 0)
        table.attach(icon, 0, 1, 0, 1, gtk.FILL)
        ########################################
        
        
        
        label=gtk.Label()
        label.set_use_markup(True)
        label.set_alignment(0, 0.5)
        label.set_justify(gtk.JUSTIFY_LEFT)
        if title not in ['reboot', 'poweroff', 'quit']:
            if "floppy" in title:
                devtype=_("Floppy: %s") %item[4]
            elif "cdrom" in title:
                devtype=_("CDROM: %s") %item[4]
            elif "usb" in title:
                devtype=_("USB: %s") %item[4]
            elif "hdd" in title:
                devtype=_("HDD partition: %s") %item[4]
            else:
                devtype=_("Unknow: %s") %item[4]
            # have device description???
            if item[6] is not None and item[6] != "unknow":
                devdesc=item[6]
            else:
                devdesc=item[0]
            label.set_markup( "<b>%s</b>\n<small>%s</small>" %(devtype, devdesc) )
            label.set_sensitive(status)
        else:
            label.set_markup("<b>%s</b>"%item[0])
        label.show()
        #table.attach(label, 1, 2, 0, 1, gtk.EXPAND, False, 0, 0)
        table.attach(label, 1, 2, 0, 1, gtk.EXPAND)
        
        ########## BUTTON ########
        
        button_image=gtk.Image()
        button=gtk.Button()
        button.set_sensitive(True)
        if title in ['reboot', 'poweroff', 'quit']:
            button_image.set_from_file(icon_file)
            #button.set_sensitive(True)
        else:
            button_image.set_from_file(tcosmonitor.shared.IMG_DIR + "eject.png")
            #button.set_sensitive(False)
        
        button.set_image(button_image)
        button.connect("clicked", self.do_action, title, item)
        button.show()
        #table.attach(button, 2, 3, 0, 1, gtk.FILL, False, 0, 0)
        table.attach(button, 2, 3, 0, 1, gtk.FILL)
        
        table.show()
        self.devbox.add(table)
        
        # add separator
        separator=gtk.HSeparator()
        self.devbox.add(separator)
        

    def close_popup(self, *args):
        #print_debug( "close_popup() args=%s" %str(args) )
        gobject.timeout_add(100, self.window.hide)

    def popup_window(self, *args):
        #print_debug("popup_window() args=%s" %str(args))
        
        # get popup size
        winx, winy = self.window.size_request()
        
        # get window size
        width=gtk.gdk.screen_width()
        height=gtk.gdk.screen_height()
        
        # get trayicon position
        a, rect, c = self.statusIcon.get_geometry()
        
        # new pos
        if rect.x + winx > width:
            #print( "rect.x=%s + winx=%s GREATER with=%s" %(rect.x, winx, width) )
            newx=abs(width-winx)
        else:
            #print( "rect.x=%s + winx=%s LOWER with=%s" %(rect.x, winx, width) )
            newx=rect.x
        
        if rect.y + winy > height:
            #print( "rect.y=%s + winy=%s GREATER que height=%s" %(rect.y, winy, height) )
            newy=abs( height-winy-(self.statusIcon.get_size()) -5 )
        else:
            #print( "rect.y=%s + winy=%s LOWER que height=%s" %(rect.y, winy, height) )
            newy=abs( rect.y-(self.statusIcon.get_size()) )
        
        # move
        self.window.move( newx, newy )
        #print "newx=%s  newy=%s"%(newx, newy)
        
        # ugly hack to avoid wrong height
        if self.first_time:
            #self.window.show()
            #self.window.hide()
            self.first_time=False
            self.popup_window()
        
        gobject.timeout_add(100, self.window.show)
        #self.window.show()

    
    def update_status(self, device, actions, status):
        print_debug ("update_status() device=%s of %s to %s" %(device, actions, status))
        
        if self.items.has_key(device):
            if "_mount" in actions and status:
                #print "  action UMOUNTING..."
                # if xxx_mount is True device is umounted
                self.items[device][5]=False
            
            if "_umount" in actions and status:
                #print "  action MOUNTING..."
                self.items[device][5]=True
            
            #print "     STATUS of %s is %s" %(device, status)
        
            self.items["%s"%device][3]["%s"%actions][2]=status
            #self.InitMenu()
            gobject.timeout_add(100, self.InitMenu)
        else:
            print_debug( " WW: no updating status of %s"%(actions) )
            
    def register_action(self, action, function, *args):
        #print_debug("register_action() action=%s function=%s, args=%s" %(action, function, args) )
        self.actions["%s" %action]=function
        self.args["%s" %action]=args
        #self.InitMenu()
        return
        
    def unregister_action(self, action):
        self.actions.pop(action)
        #self.InitMenu()
        return
    
    def register_device(self, device, devname, devimage, show, actions, devid, devdesc=None):
        if devdesc is not None:
            devdesc=devdesc.replace('_', ' ').replace('|', '')
        print_debug("register_device() device='%s' devname='%s' devimage='%s' show='%s' actions='%s' devid='%s' devdesc='%s'" 
                    %(device, devname, devimage, show, actions, devid, devdesc) )
        self.items["%s"%(device)]=[ devname, devimage, show, actions, devid, False, devdesc]
        self.InitMenu()
        #print self.items["%s"%(device)]
    
    def unregister_device(self, device):
        print_debug("unregister_device() device=%s" %(device) )
        if self.items.has_key(device):
            self.items.pop(device)
        else:
            print "WARNING: device %s not found" % device
        

    def do_action(self, widget, name, item=None):
        print_debug ("do_action() widget=%s name=%s" %(widget, name) )
        if self.actions.has_key(name):
            #print_debug("do_action() function=%s args=%s" %(self.actions[name], self.args[name]) )
            self.actions[name](self.args[name])
        else:
            if item:
                #print self.items[name][5]
                if self.items[name][5]: # mounted => umount
                    #print "umount"
                    key="%s_umount" %name
                    
                else:
                    #print "mount"
                    key="%s_mount" %name
                
                if self.actions.has_key(key):
                    self.actions[key](self.args[key])
            else:
                print "TcosTrayIcon WARNING: no menu action set for \"%s\" event" % (name)
        return






if __name__ == "__main__":

    def myprint(*args):
        print "MYPRINT %s" % args
    
    tcosmonitor.shared.debug=True
    
    def change(*args):
        systray.status = not systray.status
        systray.update_status("usb1", "usb1_mount", systray.status)
        systray.update_status("usb1", "usb1_umount", not systray.status)
    
    systray=TcosTrayIcon(disable_quit=False)

    systray.status=True

    systray.update_status("cdrom1", "cdrom1_mount", False)
    systray.update_status("cdrom1", "cdrom1_umount", False)

    #systray.register_action("quit", lambda w: gtk.main_quit() )
    systray.register_action("quit", change )
    
    systray.register_action("cdrom1_mount", myprint )
    systray.register_action("cdrom1_umount", myprint )
    
    systray.register_device("usb1", _("Usb flash"), "floppy_mount.png", True,
        {
        "usb1_mount":[ _("Mount USB1"), "floppy_mount.png", False, None, "/dev/sda1"],
        "usb1_umount":[ _("Umount USB1"), "floppy_umount.png", False, None, "/dev/sda1"],
        }, "/dev/sda1"
        )
    
    def usb(action):
        print "ACTION usb, action=%s" % action
        if action == "umount":
            print "desmontando....."
            systray.update_status("usb1", "usb1_mount", True)
            systray.update_status("usb1", "usb1_umount", False)
            print "................... desmontado"
        else:
            print "montando........"
            systray.update_status("usb1", "usb1_mount", False)
            systray.update_status("usb1", "usb1_umount", True)
            print ".................... montado"
    
    systray.update_status("usb1", "usb1_mount", True)
    systray.update_status("usb1", "usb1_umount", False)
    
    systray.register_action("usb1_umount", usb , "umount")
    systray.register_action("usb1_mount", usb  , "mount")
    #systray.register_action("usb1", change )
    
    
    gtk.main()


