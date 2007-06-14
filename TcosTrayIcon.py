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
import gtk
import os
from gettext import gettext as _

MENU_DATA=os.path.expanduser("~/.tcos-devices")

import shared

def print_debug(txt):
    if shared.debug:
        print "%d %s::%s" %(os.getpid(), __name__, txt)


def crono(start, txt):
    print_debug ("crono(), %s get %f seconds" %(txt, (time() - start)) )
    return


class TcosTrayIcon:
    def __init__(self):
        self.actions={}
        self.args={}
        self.statusIcon = gtk.StatusIcon()
        self.menu=gtk.Menu()
        self.items={ "quit": [_("Quit"), "menu_kill.png", True, None]  }
        
        self.InitMenu()
        self.InitStatusIcon()


    def InitMenu(self):
        #print_debug ("InitMenu()")
        self.menu.popdown()
        self.menu=gtk.Menu()
        menu_item = gtk.MenuItem(_("TcosDevices"))
        self.menu.append(menu_item)
        menu_item.set_sensitive(False)
        menu_item.show()
        

        sorted=self.items.keys()
        sorted.sort()
        for m in sorted:
            if m != "quit":
                self.menu.append(self.create_menu(self.items[m], m) )
                
        # add quit menu at bottom
        if self.items.has_key("quit"):
            self.menu.append(self.create_menu(self.items["quit"], "quit") )
        return
    
    def update_status(self, device, actions, status):
        print_debug ("updating status of %s to %s" %(actions, status))
        
        if self.items.has_key("%s"%device):
            self.items["%s"%device][3]["%s"%actions][2]=status
            self.InitMenu()
        else:
            print_debug( " WW: no updating status of %s"%(actions) )
            
    def register_action(self, action, function, *args):
        self.actions["%s" %action]=function
        self.args["%s" %action]=args
        #self.InitMenu()
        return
        
    def unregister_action(self, action):
        self.actions.pop(action)
        #self.InitMenu()
        return
    
    
    def register_device(self, device, devname, devimage, show, actions, devid):
        self.items["%s"%(device)]=[ devname, devimage, show, actions, devid]
        self.InitMenu()
        #print self.items["%s"%(device)]
    
    def unregister_device(self, device):
        if self.items.has_key(device):
            self.items.pop("%s"%device)
        else:
            print "WARNING: device %s not found" %device

    def create_menu(self, item, name):
        #print_debug ("   => creating menu %s for %s" %(item,name) )
        # search for icon
        icon_file_found=False
        if item[1] != None: 
            icon_file_found=True
            icon_file=shared.IMG_DIR + item[1]
            if not os.path.isfile(icon_file):
                icon_file_found=False

        
        if icon_file_found:
            # we have icon
            menu_items=gtk.ImageMenuItem(item[0], True)
            icon = gtk.Image()
            icon.set_from_file(icon_file)
            menu_items.set_image(icon)
        else:
            buf = item[0]
            menu_items = gtk.MenuItem(buf)
        
        
        menu_items.show()
        menu_items.set_sensitive(item[2])
        #print_debug("create_menu() name=%s item=%s" %(name, item))
        #print "name=%s sensitive=%s " %(name, item[2])
        
        if item[3]:
            submenu = gtk.Menu()
            
            sorted=item[3].keys()
            sorted.sort()
            
            for subitem in sorted:
                #print_debug("create_menu() name=%s item=%s" %(subitem, item[3][subitem]))
                #print_debug( "         => creando submenu %s item=%s" %(subitem, item[3][subitem]) )
                submenu.append( self.create_menu(item[3][subitem], subitem) )
                
            menu_items.set_submenu(submenu)
            #menu_items.connect("activate", self.do_action, name)        
        else:
            menu_items.connect("activate", self.do_action, name)
            
        return menu_items

    def do_action(self,widget, name):
        print_debug ("do_action() widget=%s name=%s" %(widget, name) )
        if self.actions.has_key(name):
            #print_debug("do_action() function=%s args=%s" %(self.actions[name], self.args[name]) )
            self.actions[name](self.args[name])
        else:
            print "TcosTrayIcon WARNING: no menu action set for \"%s\" event" %(name)
        return

    def InitStatusIcon(self):
        if hasattr(gtk, 'status_icon_new_from_file'):
            # use gtk.status_icon
            self.statusIcon = gtk.status_icon_new_from_file(shared.IMG_DIR + "tcos-devices-32x32.png")
            self.statusIcon.set_tooltip( _("Tcos Devices") )
            self.statusIcon.connect('popup-menu', self.popup_menu)
        else:
            # based on http://www.burtonini.com/computing/notify.py
            import egg.trayicon
            icon = egg.trayicon.TrayIcon("TCOS")
            eventbox = gtk.EventBox()
            icon.add(eventbox)
            #tcos-icon-32x32.png
            image=gtk.Image()
            image.set_from_file (shared.IMG_DIR + "tcos-devices-32x32.png")
            eventbox.add(image)
            tips = gtk.Tooltips()
            
            tips.set_tip(icon, ( _("Tcos Devices") )[0:79])
            tips.enable()
            icon.show_all()
            eventbox.connect("button_press_event", self.popup_menu2)
        return
     
    def popup_menu(self, widget, button, time):
        self.InitMenu()
        if self.menu:
            self.menu.show_all()
            self.menu.popup(None, None, None, 3, time)
        return

    def popup_menu2(self, widget, event):
        self.InitMenu()
        self.menu.popup(None, None, None, event.button, event.time)

    



if __name__ == "__main__":

    def myprint(*args):
        print "MYPRINT %s" %args
    
    shared.debug=True
    
    def change(*args):
        systray.status = not systray.status
        systray.update_status("usb1", "usb1_mount", systray.status)
        systray.update_status("usb1", "usb1_umount", not systray.status)
    
    systray=TcosTrayIcon()

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
    
    
    
    systray.update_status("usb1", "usb1_mount", True)
    systray.update_status("usb1", "usb1_umount", False)
    
    systray.register_action("usb1_umount", change )
    systray.register_action("usb1_mount", change )
    #systray.register_action("usb1", change )
    
    
    gtk.main()

