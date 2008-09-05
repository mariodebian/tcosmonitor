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

from gettext import gettext as _
import shared

# needed for get_screenshot
from time import localtime
import gtk

from TcosExtensions import TcosExtension


def print_debug(txt):
    if shared.debug:
        print "%s::%s" %("extensions::screenshot", txt)
    return


class Screenshot(TcosExtension):
    def register(self):
        self.main.menus.register_simple( _("Screenshot"), "menu_screenshot.png", 2, self.take_screenshot)
        self.main.menus.register_all( _("Capture All clients screens") , "menu_screenshot.png", 2, self.take_all_screenshots)

    ###########  SIMPLE HOST ###############

    def take_screenshot(self, widget, ip):
        if not self.get_client():
            return
        print_debug("take_screenshot() widget=%s ip=%s"%(widget,ip))
        
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
        
        
        block_txt=_("Screenshot of <span style='font-style: italic'>%s</span>")%(self.main.localdata.GetHostname(ip))
        block_txt+="<span style='font-size: medium'> %s </span>" %(datetxt)
        block_txt+="<span> </span><input type='button' name='self.main.another_screenshot_button' label='%s' />" %( slabel )
         
        self.main.common.threads_enter("TcosActions::get_screenshot show capture")
        #url="http://%s:%s/capture-thumb.jpg" %(ip, shared.httpd_port)
        self.main.datatxt.clean()
        self.main.datatxt.insert_block( block_txt )
                                 
        #self.main.datatxt.insert_html( "<img src='%s' alt='%s'/>\n"\
        #                         %(url, _("Screenshot of %s" %(ip) )) )
        
        # Use Base64 data
        self.main.datatxt.insert_html("""\n<img base64="%s" />\n"""%(scrot[1]))
        
        self.main.common.threads_leave("TcosActions::get_screenshot show capture")
        
        self.main.common.threads_enter("TcosActions::get_screenshot END")
        self.main.datatxt.display()
        self.main.write_into_statusbar ( _("Screenshot of %s, done.") %(ip)  )
        self.main.common.threads_leave("TcosActions::get_screenshot END")
        
        return False

    ###########  MULTIPLE HOSTS ###############

    def take_all_screenshots(self, widget):
        if not self.get_all_clients():
            return
        self.main.worker=shared.Workers(self.main, None, None)
        self.main.worker.set_for_all_action(self.action_for_clients, self.allclients, 'screenshot' )


    def start_action(self):
        self.main.datatxt.clean()
        self.main.datatxt.insert_block( _("Screenshots of all hosts") )
        self.main.datatxt.insert_html("<br/>")

    def real_action(self, ip, action):
        print_debug("real_action() ip=%s")
        self.main.xmlrpc.newhost(ip)
        scrot=self.main.xmlrpc.getscreenshot(self.main.config.GetVar("miniscrot_size"))
        if scrot and scrot[0] == "ok":
            hostname=self.main.localdata.GetHostname(ip)
            self.main.common.threads_enter("extensions/screenshot::real_action screenshot")
            self.main.datatxt.insert_html( 
                 "<span style='background-color:#f3d160'>" +
                 "\n\t<img base64='%s' title='%s' title_rotate='90' /> " %(scrot[1],_( "Screenshot of %s" ) %(hostname) ) +
                 "<span style='background-color:#f3d160; color:#f3d160'>__</span>\n</span>"+
                 "")
            self.main.common.threads_leave("extensions/screenshot::real_action screenshot")

    def finish_action(self):
        self.main.datatxt.display()

__extclass__=Screenshot








