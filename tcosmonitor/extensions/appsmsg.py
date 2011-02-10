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
""" template extension """

from gettext import gettext as _

from tcosmonitor import shared
from tcosmonitor.TcosExtensions import TcosExtension

import gtk
from time import time
import os
import sys
import glob

def print_debug(txt):
    if shared.debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)

def crono(start, txt):
    print_debug ("crono(), %s get %f seconds" %(txt, (time() - start)) )
    return

class AppsAndMsgs(TcosExtension):
    def register(self):
        self.init_ask()
        self.main.classview.class_external_exe=self.exe_app_external
        self.main.actions.button_action_exe=self.exe_app_all
        self.main.actions.button_action_text=self.send_msg_all
        
        self.main.menus.register_simple( _("Exec app on user display") , "menu_exec.png", 1, self.exe_app, "exe")
        self.main.menus.register_simple( _("Send a text message to user") , "menu_msg.png", 1, self.send_msg, "text")
        
        self.main.menus.register_all( _("Exec same app in all connected users") , "menu_exec.png", 1, self.exe_app_all, "exe")
        self.main.menus.register_all( _("Send a text message to all connected users") , "menu_msg.png", 1, self.send_msg_all, "text")

##############################################################################
    def askfor(self, mode="mess", msg="", users=None, users_txt=None):
        if users == None or users_txt == None:
            users=[]
        self.ask_usernames=[]
        if len(users) == 0 or users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg( _("Clients not connected") )
            return
        else:
            self.ask_usernames=users

        #users_txt=""
        #counter=1
        #for user in self.ask_usernames:
        #    users_txt+="%s, " %(user)
        #    print_debug("askfor() counter=%s" %(counter) )
        #    if counter % 4 == 0:
        #        users_txt+="\n"
        #    counter=int(counter+1)

        #if users_txt[-2:] == "\n": users_txt=users_txt[:-2]
        #if users_txt[-2:] == ", ": users_txt=users_txt[:-2]
        
        if mode == "exec":
            # enable drag & drop
            self.main.ask_fixed.show()
            self.main.ask_dragdrop.show()
            self.main.image_entry.show()
            self.main.image_entry.set_from_stock(gtk.STOCK_DIALOG_QUESTION, 4)
            self.main.ask_label.set_markup( _("<b>Exec app in user(s) screen(s)\nor open web address to:</b>\n%s" ) %( users_txt ) )
        elif mode == "mess":
            self.main.ask_label.set_markup( _("<b>Send a message to:</b>\n%s" ) %( users_txt ) )
        elif mode == "any":
            self.main.ask_label.set_markup( msg )
        self.ask_mode=mode
        self.main.ask.show()
        return True


    def on_ask_exec_click(self, widget):
        app=self.main.ask_entry.get_text()
        if app != "":
            self.exe_app_in_client_display(app)
        return


    def on_ask_cancel_click(self, widget):
        self.main.ask.hide()
        self.main.ask_entry.set_text("")
        # disable drag & drop
        self.main.ask_fixed.hide()
        self.main.image_entry.hide()
        self.main.ask_dragdrop.hide()
        return
##############################################################################

    def exe_app_external(self, filename=None, txt=None):
        if self.main.classview.ismultiple() or txt != None:
            if not self.get_all_clients():
                return
        elif not self.get_client():
            return

        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg ( _("Can't exec application, user is not logged") )
            return
        #print_debug("user=%s data=%s" %(self.connected_users, data)
        app=""
        self.ask_usernames=self.connected_users
        self.ask_mode="exec"

        if txt != None:
            app="x-www-browser %s" %txt
            self.exe_app_in_client_display(app)
            return
        
        print_debug("open_file() reading data from \"%s\"..." \
                        %(filename) )
        try:
            fd=file(filename, 'r')
            data=fd.readlines()
            fd.close()
        except Exception, err:
            shared.error_msg( _("%s is not a valid application") %(os.path.basename(filename)) )
            return
        
        for line in data:
            if line != '\n':
                if line.startswith("Exec="):
                    line=line.replace('\n', '')
                    action, app=line.split("=",1)
                    app=app.replace("%U","").replace("%u","").replace("%F","").replace("%f","").replace("%c","").replace("%i","").replace("%m","")
                                    
        if len(app) <1:
            shared.error_msg( _("%s is not a valid application") %(os.path.basename(filename)) )

        if app != "":
            self.exe_app_in_client_display(app)
        return
    

    def exe_app(self, w, ip):
        if not self.get_client():
            return
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg ( _("Can't exec application, user is not logged") )
            return
        self.askfor(mode="exec", users=self.connected_users, users_txt=self.connected_users_txt)


    def send_msg(self, w, ip):
        if not self.get_client():
            return
        if len(self.connected_users) == 0 or self.connected_users[0] == shared.NO_LOGIN_MSG:
            shared.error_msg ( _("Can't send message, user is not logged") )
            return
        self.askfor(mode="mess", users=self.connected_users, users_txt=self.connected_users_txt)

    def exe_app_all(self, *args):
        if not self.get_all_clients():
            return
        self.askfor(mode="exec", users=self.connected_users, users_txt=self.connected_users_txt)

    def send_msg_all(self, *args):
        if not self.get_all_clients():
            return
        self.askfor(mode="mess", users=self.connected_users, users_txt=self.connected_users_txt)


####################### INIT ############################################
    def init_ask(self):
        self.main.ask_ip=None
        
        self.ui = gtk.Builder()
        self.ui.set_translation_domain(shared.PACKAGE)
        self.ui.add_from_file(shared.GLADE_DIR + 'tcosmonitor-askwindow.ui')
        
        self.main.ask = self.ui.get_object('askwindow')
        self.main.ask.connect('delete-event', self.askwindow_close )
        self.main.ask.set_icon_from_file(shared.IMG_DIR +'tcos-icon-32x32.png')
        
        
        self.main.ask_label = self.ui.get_object('txt_asklabel')
        ## arrastrar y soltar
        self.main.ask_fixed = self.ui.get_object('ask_fixed')
        self.main.ask_dragdrop = self.ui.get_object('label99')
        self.main.image_entry = self.ui.get_object('image_askentry')
        self.main.image_entry.drag_dest_set( gtk.DEST_DEFAULT_ALL, [( 'text/uri-list', 0, 2 ), ], gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_COPY)
        self.main.image_entry.connect( 'drag_data_received', self.on_drag_data_received)
        self.main.ask_fixed.hide()
        self.main.image_entry.hide()
        self.main.ask_dragdrop.hide()
        ## fin arrastrar y soltar
        self.liststore = gtk.ListStore(str)
        for s in shared.appslist:
            self.liststore.append([s])
            
        self.main.ask_entry = self.ui.get_object('txt_askentry')
        self.main.ask_completion = gtk.EntryCompletion()
        self.main.ask_completion.set_model(self.liststore)
        self.main.ask_entry.set_completion(self.main.ask_completion)
        self.main.ask_completion.set_text_column(0)
        
        self.main.ask_completion.connect('match-selected', self.match_cb)
        self.main.ask_entry.connect('activate', self.activate_cb)
        
        self.main.ask_cancel = self.ui.get_object('ask_cancelbutton')
        self.main.ask_exec = self.ui.get_object('ask_exebutton')
        
        # buttons signals
        self.main.ask_exec.connect('clicked', self.on_ask_exec_click)
        self.main.ask_cancel.connect('clicked', self.on_ask_cancel_click)


    def askwindow_close(self, widget, event):
        print_debug ( "askwindow_close() closing ask window" )
        self.main.ask.hide()
        return True

    def on_drag_data_received( self, widget, context, x, y, selection, targetType, dtime):
        files = selection.data.split('\n', 1)
        start1=time()
        print_debug("on_drag_data_received() files=%s dtime=%s"%(files, dtime))
        for f in files:
            if f:
                desktop = f.strip().replace('%20', ' ')
                break
                   
        if desktop.startswith('file:///') and desktop.lower().endswith('.desktop') and os.path.isfile(desktop[7:]):
            print_debug("open_file() reading data from \"%s\"..." \
                        %(desktop[7:]) )
            fd=file(desktop[7:], 'r')
            data=fd.readlines()
            fd.close()
            
            # try to load gnome theme with gconf
            mytheme=[]
            theme=self.main.common.get_icon_theme()
            print_debug("on_drag_data_received() gconf theme=%s"%theme)
            
            str_image=""
            files=[]
            
            if theme and os.path.isdir("/usr/share/icons/%s"%theme):
                files+=glob.glob("/usr/share/icons/%s/48x48/*.png"%(theme))
            
            files+=glob.glob("/usr/share/icons/hicolor/48x48/*/*.png") + \
                glob.glob("/usr/share/icons/gnome/48x48/*/*.png") + \
                glob.glob("/usr/share/pixmaps/*png") +\
                glob.glob("/usr/share/pixmaps/*xpm")
            
            for line in data:
                if line != '\n':
                    if line.startswith("Exec="):
                        line=line.replace('\n', '')
                        action, str_exec=line.split("=",1)
                        str_exec=str_exec.replace("%U","").replace("%u","").replace("%F","").replace("%f","").replace("%c","").replace("%i","").replace("%m","")
                    elif line.startswith("Icon="):
                        line=line.replace('\n', '')
                        action, image_name=line.split("=",1)                        
                        if not os.path.isfile(image_name):
                            start2=time()
                            for f in files:
                                if image_name in f or image_name.replace('_', '-') in f:
                                    str_image=f
                                    crono(start2, "on_drag_data_received() ICON FOUND AT %s"%f )
                                    break
                        else:
                            str_image=image_name
                                    
            if len(str_exec) <1:
                shared.error_msg( _("%s is not application") %(os.path.basename(desktop[7:])) )
            else:
                if len(str_image) <1:
                    print_debug("on_drag_data_received() image '%s' not found"%image_name)
                    self.main.image_entry.set_from_stock(gtk.STOCK_DIALOG_QUESTION, 4)
                else:
                    self.main.image_entry.set_from_file(str_image)
                self.main.ask_entry.set_text(str_exec)
        else:
            shared.error_msg( _("%s is not application") %(os.path.basename(desktop[7:])) )
        crono(start1, "on_drag_data_received() end" )
        return True

    def match_cb(self, completion, model, iter):
        print_debug ( "match_cb() " )
        print_debug( "%s was selected" %(model[iter][0]) )
        self.exe_app_in_client_display(model[iter][0])
        return


    def activate_cb(self, entry):
        text = self.main.ask_entry.get_text()
        print_debug ( "activate_cb() text=%s" %(text) )
        
        # append to liststore
        if text:
            if text not in [row[0] for row in self.liststore]:
                self.liststore.append([text])
                #self.main.ask_entry.set_text('')
        
        # exe app
        self.exe_app_in_client_display(text)
        return

    def exe_app_in_client_display(self, arg):
        usernames=self.ask_usernames
        newusernames=[]
        print_debug("exe_app_in_client_display() usernames=%s" %usernames)
        
        if arg.startswith('rm ') or arg.find(" rm ") != -1 \
                or arg.startswith('mv ') or arg.find(" mv ") != -1 \
                or arg.startswith('cp ') or arg.find(" cp ") != -1:
            arg=""
        
        #if self.ask_mode == "mess":
        #    arg=arg.replace("'", "´")
        if self.ask_mode == "exec":
            if arg.startswith('http://') or arg.startswith('https://') or arg.startswith('ftp://'):
                arg="xdg-open %s" %arg
            
        for user in usernames:
            if user.find(":") != -1:
                # we have a standalone user...
                usern, ip = user.split(":")
                print_debug("exe_app_in_client_display() STANDALONE username=%s ip=%s" %(usern, ip))
                self.main.xmlrpc.newhost(ip)
                self.main.xmlrpc.DBus(self.ask_mode, arg)
            else:
                newusernames.append(user)
   
        # we have a thin client user
        if self.ask_mode == "exec":
            result = self.main.dbus_action.do_exec( newusernames , arg )
            if not result:
                shared.error_msg ( _("Error while exec remote app:\nReason: %s") %( self.main.dbus_action.get_error_msg() ) )
            else:
                self.main.ask.hide()
                self.main.ask_entry.set_text("")
        elif self.ask_mode == "mess":
            result = self.main.dbus_action.do_message( newusernames , arg)
            if not result:
                shared.error_msg ( _("Error while send message:\nReason: %s") %( self.main.dbus_action.get_error_msg() ) )
        self.main.ask_dragdrop.hide()
        self.main.ask_fixed.hide()
        self.main.image_entry.hide()
        self.main.ask.hide()
        self.main.ask_entry.set_text("")
        dbus_action=None
        self.ask_mode=None
        return

__extclass__=AppsAndMsgs






