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

#import gobject
import gtk
from gettext import gettext as _
#import os,subprocess
import os
#import string

import shared

menus_group = [
    [ 0, _("Terminal actions") , "active.png"],
    [ 1, _("User actions") , "logged.png"],
    [ 2, _("Audio, video and files"), "multimedia.png"],
]

def print_debug(txt):
    if shared.debug:
        print "%s::%s" % (__name__, txt)

class TcosMenus(object):
    def __init__(self, main):
        print_debug("__init__()")
        self.main=main
        self.ui=self.main.ui
        
        self.simplemenus=[]
        self.allmenus=[]
        
        self.main.menu=gtk.Menu()
        self.main.allmenu=gtk.Menu()

        #self.broadcast_count={}

    def register_simple(self, name, icon, group, action, func_name):
        #print_debug("register_simple() name=%s, icons=%s, group=%s, action=%s" %(name, icon, group, action))
        self.simplemenus.append( [name, icon, group, action, func_name] )
        #print_debug("%s" %[name, icon, group, action, func_name] )

    def register_all(self, name, icon, group, action, func_name):
        #print_debug("register_all() name=%s, icons=%s, group=%s, action=%s" %(name, icon, group, action))
        self.allmenus.append( [name, icon, group, action, func_name] )

    def MustShowMenu(self, func_name, menutype):
        item_name="ck_menu_%s" %func_name

        if not item_name in shared.preferences_menus:
            #print_debug("MustShowMenu() %s %s NOT FOUND return True item_name=%s" %(func_name, menutype, item_name) )
            return True

        if menutype == "menuone":
            for number in shared.preferences_menus[item_name][1]:
                if number in shared.preferences_menus_always_show[menutype]:
                    #print_debug("MustShowMenu() %s %s FOUND in MENUONE return True" %(func_name, menutype) )
                    return True 
       
        if menutype == "menuall":
            for number in shared.preferences_menus[item_name][2]:
                if number in shared.preferences_menus_always_show[menutype]:
                    #print_debug("MustShowMenu() %s %s found in MENUALL return True" %(func_name, menutype) )
                    return True

        if func_name in self.main.preferences.visible_menu_items["names"]:
            #print_debug("MustShow() number %s found at %s menutype %s"%(number, self.main.preferences.visible_menu_items[menutype], menutype))
            return True
        #print_debug("MustShowMenu() %s %s return False item_name=%s" %(func_name, menutype, item_name) )
        return False

    def RightClickMenuOne(self, path=None, model=None, ip=None):
        """ menu for one client"""
        print_debug ( "RightClickMenuOne() creating menu" )
        self.main.menu=gtk.Menu()
        
        #print_debug ("%s"%self.simplemenus)
        
        totalhidemenus=0
        #menu header
        if ip:
            menu_items = gtk.MenuItem( _("Actions for %s") %(ip) )
            self.main.menu.append(menu_items)
            menu_items.set_sensitive(False)
            menu_items.show()
        elif path == None:
            menu_items = gtk.MenuItem(_("Actions for selected host"))
            self.main.menu.append(menu_items)
            menu_items.set_sensitive(False)
            menu_items.show()
        else:
            if not model:
                model=self.main.tabla.get_model()
            menu_items = gtk.MenuItem( _("Actions for %s") %(model[path][1]) )
            ip=model[path][1]
            self.main.menu.append(menu_items)
            menu_items.set_sensitive(False)
            menu_items.show()
        
        for mainmenu in menus_group:
            if mainmenu[2] != None and os.path.isfile(shared.IMG_DIR + mainmenu[2]):
                menu_item = gtk.ImageMenuItem(mainmenu[1], True)
                icon = gtk.Image()
                icon.set_from_file(shared.IMG_DIR + mainmenu[2])
                menu_item.set_image(icon)
            else:
                menu_item=gtk.MenuItem(mainmenu[1])
            
            submenu = gtk.Menu()
            count=0
            # parse submenu items and create submenu
            for _s in self.simplemenus:
                if _s[2] != mainmenu[0]:
                    continue
                if _s[1] != None and os.path.isfile(shared.IMG_DIR + _s[1]):
                    sub = gtk.ImageMenuItem(_s[0], True)
                    icon = gtk.Image()
                    icon.set_from_file(shared.IMG_DIR + _s[1])
                    sub.set_image(icon)
                else:
                    sub=gtk.MenuItem(_s[0])
                # show ???
                if self.MustShowMenu(_s[4], "menuone"):
                    #print_debug("RightClickMenuOne()    [SHOW] %s"%_s)
                    sub.connect("activate", _s[3], ip)
                    sub.show()
                    count+=1
                else:
                    #print_debug("RightClickMenuOne()    [HIDE] %s"%_s)
                    sub.hide()
                    totalhidemenus+=1
                if self.main.config.GetVar("menugroups") == 1:
                    #print_debug("RightClickMenuOne() MENU GROUPS")
                    submenu.append(sub)
                else:
                    #print_debug("RightClickMenuOne() PLAIN MENU")
                    self.main.menu.append(sub)
            menu_item.set_submenu(submenu)
            # if submenu is empty don't show
            if count == 0:
                menu_item.hide()
            else:
                menu_item.show()
            # append to main menu
            if self.main.config.GetVar("menugroups") == 1:
                self.main.menu.append(menu_item)
        if totalhidemenus > 0:
            hide_items = gtk.MenuItem(_("%d hidden actions") %totalhidemenus)
            hide_items.set_sensitive(False)
            hide_items.show()
            self.main.menu.append(hide_items)
        return
#        """
#        
#        #add all items in shared.onehost_menuitems
#        # shared.allhost_mainmenus contains menu groups
#        # [0] = menu group name
#        # [1] = menu group icon
#        # [2] = menu group submenus (index of shared.allhost_menuitems)
#        for mainmenu in shared.onehost_mainmenus:
#            #print_debug("RightClickMenuOne() %s"%mainmenu)
#            # create menu gropu entry (with icon or not)
#            if mainmenu[1] != None and os.path.isfile(shared.IMG_DIR + mainmenu[1]):
#                menu_item = gtk.ImageMenuItem(mainmenu[0], True)
#                icon = gtk.Image()
#                icon.set_from_file(shared.IMG_DIR + mainmenu[1])
#                menu_item.set_image(icon)
#            else:
#                menu_item=gtk.MenuItem(mainmenu[0])
#            
#            submenu = gtk.Menu()
#            count=0
#            # parse submenu items and create submenu
#            for i in mainmenu[2]:
#                _s=shared.onehost_menuitems[i]
#                if _s[1] != None and os.path.isfile(shared.IMG_DIR + _s[1]):
#                    sub = gtk.ImageMenuItem(_s[0], True)
#                    icon = gtk.Image()
#                    icon.set_from_file(shared.IMG_DIR + _s[1])
#                    sub.set_image(icon)
#                else:
#                    sub=gtk.MenuItem(_s[0])
#                # show ???
#                if self.MustShowMenu(i, "menuone"):
#                    #print_debug("RightClickMenuOne()    [SHOW] %s"%_s)
#                    sub.connect("activate", self.on_rightclickmenuone_click, i)
#                    sub.show()
#                    count+=1
#                else:
#                    #print_debug("RightClickMenuOne()    [HIDE] %s"%_s)
#                    sub.hide()
#                    totalhidemenus+=1
#                if self.main.config.GetVar("menugroups") == 1:
#                    #print_debug("RightClickMenuOne() MENU GROUPS")
#                    submenu.append(sub)
#                else:
#                    #print_debug("RightClickMenuOne() PLAIN MENU")
#                    self.main.menu.append(sub)
#            menu_item.set_submenu(submenu)
#            # if submenu is empty don't show
#            if count == 0:
#                menu_item.hide()
#            else:
#                menu_item.show()
#            # append to main menu
#            if self.main.config.GetVar("menugroups") == 1:
#                self.main.menu.append(menu_item)
#        if totalhidemenus > 0:
#            hide_items = gtk.MenuItem(_("%d hidden actions") %totalhidemenus)
#            hide_items.set_sensitive(False)
#            hide_items.show()
#            self.main.menu.append(hide_items)
#        return
#        """
        
    def RightClickMenuAll(self):
        """ menu for ALL clients"""
        self.main.allmenu=gtk.Menu()
        
        totalhidemenus=0
        #menu headers
        if self.main.config.GetVar("selectedhosts") == 1:
            menu_items = gtk.MenuItem(_("Actions for selected hosts"))
        elif self.main.iconview.ismultiple() or self.main.classview.ismultiple():
            menu_items = gtk.MenuItem(_("Actions for selected hosts"))
        else:
            menu_items = gtk.MenuItem(_("Actions for all hosts"))
        self.main.allmenu.append(menu_items)
        menu_items.set_sensitive(False)
        menu_items.show()
        
        
        for mainmenu in menus_group:
            if mainmenu[2] != None and os.path.isfile(shared.IMG_DIR + mainmenu[2]):
                menu_item = gtk.ImageMenuItem(mainmenu[1], True)
                icon = gtk.Image()
                icon.set_from_file(shared.IMG_DIR + mainmenu[2])
                menu_item.set_image(icon)
            else:
                menu_item=gtk.MenuItem(mainmenu[1])
            
            submenu = gtk.Menu()
            count=0
            # parse submenu items and create submenu
            for _s in self.allmenus:
                if _s[2] != mainmenu[0]:
                    continue
                if _s[1] != None and os.path.isfile(shared.IMG_DIR + _s[1]):
                    sub = gtk.ImageMenuItem(_s[0], True)
                    icon = gtk.Image()
                    icon.set_from_file(shared.IMG_DIR + _s[1])
                    sub.set_image(icon)
                else:
                    sub=gtk.MenuItem(_s[0])
                if self.MustShowMenu(_s[4], "menuall"):
                    #print_debug("RightClickMenuOne()    [SHOW] %s"%_s)
                    sub.connect("activate", _s[3], )
                    sub.show()
                    count+=1
                else:
                    sub.hide()
                    totalhidemenus+=1
                if self.main.config.GetVar("menugroups") == 1:
                    #print_debug("RightClickMenuAll() MENU GROUPS")
                    submenu.append(sub)
                else:
                    #print_debug("RightClickMenuAll() PLAIN MENU")
                    self.main.allmenu.append(sub)
            menu_item.set_submenu(submenu)
            # if submenu is empty don't show
            if count == 0:
                menu_item.hide()
            else:
                menu_item.show()
            # append to main allmenu
            if self.main.config.GetVar("menugroups") == 1:
                self.main.allmenu.append(menu_item)
        if totalhidemenus > 0:
            hide_items = gtk.MenuItem(_("%d hidden actions") %totalhidemenus)
            hide_items.set_sensitive(False)
            hide_items.show()
            self.main.allmenu.append(hide_items)
        if self.main.classview.isactive():
            save_pos = gtk.ImageMenuItem(_("Save hosts positions"), True)
            icon = gtk.Image()
            icon.set_from_stock (gtk.STOCK_SAVE, gtk.ICON_SIZE_BUTTON)
            save_pos.set_image(icon)
            save_pos.connect("activate", self.main.classview.savepos, "save")
            save_pos.show()
            self.main.allmenu.append(save_pos)
            
            reset_pos = gtk.ImageMenuItem(_("Reset hosts positions"), True)
            icon = gtk.Image()
            icon.set_from_stock (gtk.STOCK_REFRESH, gtk.ICON_SIZE_BUTTON)
            reset_pos.set_image(icon)
            reset_pos.connect("activate", self.main.classview.savepos, "reset")
            reset_pos.show()
            self.main.allmenu.append(reset_pos)
        return
#        """
#        # shared.allhost_mainmenus contains menu groups
#        # [0] = menu group name
#        # [1] = menu group icon
#        # [2] = menu group submenus (index of shared.allhost_menuitems)
#        for mainmenu in shared.allhost_mainmenus:
#            # create menu gropu entry (with icon or not)
#            if mainmenu[1] != None and os.path.isfile(shared.IMG_DIR + mainmenu[1]):
#                menu_item = gtk.ImageMenuItem(mainmenu[0], True)
#                icon = gtk.Image()
#                icon.set_from_file(shared.IMG_DIR + mainmenu[1])
#                menu_item.set_image(icon)
#            else:
#                menu_item=gtk.MenuItem(mainmenu[0])
#            
#            submenu = gtk.Menu()
#            count=0
#            # parse submenu items and create submenu
#            for i in mainmenu[2]:
#                _s=shared.allhost_menuitems[i]
#                if _s[1] != None and os.path.isfile(shared.IMG_DIR + _s[1]):
#                    sub = gtk.ImageMenuItem(_s[0], True)
#                    icon = gtk.Image()
#                    icon.set_from_file(shared.IMG_DIR + _s[1])
#                    sub.set_image(icon)
#                else:
#                    sub=gtk.MenuItem(_s[0])
#                # show ???
#                if self.MustShowMenu(i, "menuall"):
#                    sub.connect("activate", self.on_rightclickmenuall_click, i)
#                    sub.show()
#                    count+=1
#                else:
#                    sub.hide()
#                    totalhidemenus+=1
#                if self.main.config.GetVar("menugroups") == 1:
#                    #print_debug("RightClickMenuAll() MENU GROUPS")
#                    submenu.append(sub)
#                else:
#                    #print_debug("RightClickMenuAll() PLAIN MENU")
#                    self.main.allmenu.append(sub)
#            menu_item.set_submenu(submenu)
#            # if submenu is empty don't show
#            if count == 0:
#                menu_item.hide()
#            else:
#                menu_item.show()
#            # append to main allmenu
#            if self.main.config.GetVar("menugroups") == 1:
#                self.main.allmenu.append(menu_item)
#        if totalhidemenus > 0:
#            hide_items = gtk.MenuItem(_("%d hidden actions") %totalhidemenus)
#            hide_items.set_sensitive(False)
#            hide_items.show()
#            self.main.allmenu.append(hide_items)
#        if self.main.classview.isactive():
#            save_pos = gtk.ImageMenuItem(_("Save hosts positions"), True)
#            icon = gtk.Image()
#            icon.set_from_stock (gtk.STOCK_SAVE, gtk.ICON_SIZE_BUTTON)
#            save_pos.set_image(icon)
#            save_pos.connect("activate", self.main.classview.savepos, "save")
#            save_pos.show()
#            self.main.allmenu.append(save_pos)
#            
#            reset_pos = gtk.ImageMenuItem(_("Reset hosts positions"), True)
#            icon = gtk.Image()
#            icon.set_from_stock (gtk.STOCK_REFRESH, gtk.ICON_SIZE_BUTTON)
#            reset_pos.set_image(icon)
#            reset_pos.connect("activate", self.main.classview.savepos, "reset")
#            reset_pos.show()
#            self.main.allmenu.append(reset_pos)
#        return
#        """

    def on_rightclickmenuone_click(self, menu, number):
        print_debug ( "on_rightclickmenuone_click() => onehost_menuitems[%d]=%s" \
                        % (number, shared.onehost_menuitems[number][0]) )
        self.main.actions.menu_event_one(number)

    def on_rightclickmenuall_click(self, menu, number):
        print_debug ( "on_rightclickmenuall_click() => allhost_menuitems[%d]=%s" \
                        % (number, shared.allhost_menuitems[number][0]) )
        self.main.actions.menu_event_all(number)

