# -*- coding: UTF-8 -*-
#    TcosMonitor version __VERSION__
#
# Copyright (c) 2006-2011 Mario Izquierdo <mariodebian@gmail.com>
#
# This package is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
#
# This package is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from gettext import gettext as _


# needed for get_screenshot
from time import localtime
import gtk
import os
import sys

from tcosmonitor import shared
from tcosmonitor.TcosExtensions import TcosExtension


def print_debug(txt):
    if shared.debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)


class Screenshot(TcosExtension):
    def register(self):
        self.main.menus.register_simple( _("Screenshot"), "menu_screenshot.png", 2, self.take_screenshot, "screenshots")
        self.main.menus.register_all( _("Capture All clients screens") , "menu_screenshot.png", 2, self.take_all_screenshots, "screenshots")
        self.main.screenshots_action=None
        self.__screenshot_counter=0
        self.__screenshot_data={}

    ###########  SIMPLE HOST ###############

    def take_screenshot(self, widget, ip):
        if not self.get_client():
            return
        print_debug("take_screenshot() widget=%s ip=%s"%(widget, ip))
        
        self.main.worker=shared.Workers(self.main, target=self.get_screenshot, args=(ip,) )
        self.main.worker.start()

    def get_screenshot(self, ip):
        self.main.xmlrpc.newhost(ip)
        if not self.main.xmlrpc.connected:
            print_debug ( "get_screenshot(%s) NO CONNECTION" %(ip) )
            self.main.common.threads_enter("TcosActions::get_screenshot writing error msg")
            self.main.write_into_statusbar( _("Can't make screenshot, error: %s") %"NO CONNECTION" )
            self.main.common.threads_leave("TcosActions::get_screenshot writing error msg")
            return
        
        # get_size
        print_debug ( "get_screenshot() scrot_size=%s" %(self.main.config.GetVar("scrot_size")) )
        
        # write into statusbar   
        self.main.common.threads_enter("TcosActions::get_screenshot writing wait msg")
        self.main.write_into_statusbar ( _("Trying to order terminal to do a screenshot...") )
        self.main.common.threads_leave("TcosActions::get_screenshot writing wait msg")
        
        # use Base64 screenshot
        scrot=self.main.xmlrpc.getscreenshot( self.main.config.GetVar("scrot_size") )
        if scrot[0] != "ok":
        #if not self.main.xmlrpc.screenshot( self.main.config.GetVar("scrot_size") ):
            self.main.common.threads_enter("TcosActions::get_screenshot writing error msg")
            self.main.write_into_statusbar( _("Can't make screenshot, error: %s") %scrot[1] )
            self.main.common.threads_leave("TcosActions::get_screenshot writing error msg")
            return False
        
        slabel=_("Get another screenshot")
        self.main.common.threads_enter("TcosActions::get_screenshot creating button")
        self.main.another_screenshot_button=None
        self.main.another_screenshot_button=gtk.Button(label=slabel )
        self.main.another_screenshot_button.connect("clicked", self.take_screenshot, ip)
        self.main.another_screenshot_button.show()
        self.main.common.threads_leave("TcosActions::get_screenshot creating button")
            
        
        print_debug ( "get_screenshot() creating button..." )
        year, month, day, hour, minute, seconds ,wdy, yday, isdst= localtime()
        datetxt="%02d/%02d/%4d %02d:%02d:%02d" %(day, month, year, hour, minute, seconds)
        print_debug ( "get_screenshot() date=%s" %(datetxt) )
        
        hostname=self.main.localdata.GetUsername(ip)
        if hostname == shared.NO_LOGIN_MSG:
            hostname=self.main.localdata.GetHostname(ip)
        block_txt=_("Screenshot of <span style='font-style: italic'>%s</span>")%(hostname)
        block_txt+="<span style='font-size: medium'> %s </span>" %(datetxt)
        block_txt+="<span> </span><input type='button' name='self.main.another_screenshot_button' label='%s' />" %( slabel )
         
        self.main.common.threads_enter("TcosActions::get_screenshot show capture")
        #url="http://%s:%s/capture-thumb.jpg" %(ip, shared.httpd_port)
        self.main.datatxt.clean()
        self.main.datatxt.insert_block( block_txt )
                                 
        #self.main.datatxt.insert_html( "<img src='%s' alt='%s'/>\n"\
        #                         %(url, _("Screenshot of %s" %(ip) )) )
        
        # Use Base64 data
        self.main.screenshots_action=self.on_screenshot_click
        self.__screenshot_counter=0
        savedatetxt="%02d-%02d-%4d_%02d-%02d" %(day, month, year, hour, minute)
        self.__screenshot_data["%s"%self.__screenshot_counter]={'hostname':hostname, 'ip':ip, 'date':savedatetxt}
        self.main.datatxt.insert_html("""\n<img onclick="%s" base64="%s" />\n"""%(self.__screenshot_counter, scrot[1]))
        
        self.main.common.threads_leave("TcosActions::get_screenshot show capture")
        
        self.main.common.threads_enter("TcosActions::get_screenshot END")
        self.main.datatxt.display()
        self.main.write_into_statusbar ( _("Screenshot of %s, done.") %(ip)  )
        self.main.common.threads_leave("TcosActions::get_screenshot END")
        
        return False

    def on_screenshot_click(self, eventbox, event, number, pixbuf):
        if event.button == 3:
            ip=self.__screenshot_data[number]['ip']
            self.main.force_selected_ip=ip
            # right click show menu
            self.main.menus.RightClickMenuOne( None , None, ip)
            self.main.menu.popup( None, None, None, event.button, event.time)
            return True
        menu=gtk.Menu()
        save_scrot = gtk.ImageMenuItem(_("Save Screenshot"), True)
        icon = gtk.Image()
        icon.set_from_stock (gtk.STOCK_SAVE, gtk.ICON_SIZE_BUTTON)
        save_scrot.set_image(icon)
        save_scrot.connect("activate", self.save_screenshot, number, pixbuf)
        save_scrot.show()
        menu.append(save_scrot)
        menu.popup( None, None, None, event.button, event.time)

    def save_screenshot(self, image, number, pixbuf):
        data=self.__screenshot_data[number]
        
        dialog = gtk.FileChooserDialog(title=_("Select file to save screenshot..."),
                                      action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                      buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_current_name( _("screenshot_of_%(hostname)s_date_%(date)s.png") %{'hostname':data['hostname'], 'date':data['date']} )
        folder = _folder = os.environ['HOME']
        dialog.set_current_folder(folder)
        _filter = gtk.FileFilter()
        _filter.set_name( _("Image Files ( *.png, *.jpg)") )
        file_types=["*.png", "*.jpg"]
        for elem in file_types:
            _filter.add_pattern( elem )
        dialog.add_filter(_filter)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            filename=dialog.get_filename()
            fext=filename.split('.')[-1]
            if not fext in ['png', 'jpg']:
                shared.error_msg( _("File must be png or jpg.") )
                dialog.destroy()
                return
            params={}
#            if fext == "jpeg":
#                {"quality":"100"}
            pixbuf.save(filename, fext, params)
        dialog.destroy()

    ###########  MULTIPLE HOSTS ###############

    def take_all_screenshots(self, widget):
        if not self.get_all_clients():
            return
        self.main.screenshots_action=self.on_screenshot_click
        self.main.worker=shared.Workers(self.main, None, None)
        self.main.worker.set_for_all_action(self.action_for_clients, self.allclients, 'screenshot' )


    def start_action(self, *args):
        self.__screenshot_counter=0
        self.__screenshot_data={}
        self.main.datatxt.clean()
        self.main.datatxt.insert_block( _("Screenshots of all hosts") )
        self.main.datatxt.insert_html("<br/>")

    def real_action(self, ip, action):
        print_debug("real_action() ip=%s" %ip)
        self.main.xmlrpc.newhost(ip)
        scrot=self.main.xmlrpc.getscreenshot(self.main.config.GetVar("miniscrot_size"))
        if scrot and scrot[0] == "ok":
            self.__screenshot_counter+=1
            hostname=self.main.localdata.GetUsername(ip)
            if hostname == shared.NO_LOGIN_MSG:
                hostname=self.main.localdata.GetHostname(ip)
            self.main.common.threads_enter("extensions/screenshot::real_action screenshot")
            year, month, day, hour, minute, seconds ,wdy, yday, isdst= localtime()
            savedatetxt="%02d-%02d-%4d_%02d-%02d" %(day, month, year, hour, minute)
            self.__screenshot_data["%s"%self.__screenshot_counter]={'hostname':hostname, 'ip':ip, 'date':savedatetxt}
            self.main.datatxt.insert_html( 
                 "<span style='background-color:#f3d160'>" +
                 "\n\t<img onclick='%s' base64='%s' title='%s' title_rotate='90' /> " %(self.__screenshot_counter, scrot[1],_( "Screenshot of %s" ) %(hostname) ) +
                 "<span style='background-color:#f3d160; color:#f3d160'>__</span>\n</span>"+
                 "")
            self.main.common.threads_leave("extensions/screenshot::real_action screenshot")

    def finish_action(self, *args):
        self.main.datatxt.display()

__extclass__=Screenshot








