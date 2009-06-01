# -*- coding: UTF-8 -*-
##########################################################################
# TcosMonitor writen by MarioDebian <mariodebian@gmail.com>
#
# TcosMonitor version __VERSION__
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
from gettext import gettext as _



import shared
import os

def print_debug(txt):
    if shared.debug:
        print "%s::%s" % (__name__, txt)

class TcosClassView(object):
    def __init__(self, main):
        print_debug("__init__()")
        self.main=main
        self.ui=self.main.ui
        self.hosts={}
        self.__selected_icon=None
        self.selected=[]
        self.class_external_exe=None
        self.class_external_video=None
        self.class_external_send=None
        self.avalaible_info=[
                    [_("IP"), 'ip' ],
                    [ _("Hostname"), 'hostname' ],
                    [ _("Username"), 'username'],
                    [ _("Logged"), 'logged'],
                    [ _("Time log in"), 'time_logged'],
                    [ _("Screen locked"), 'blocked_screen'],
                    [ _("Network locked"), 'blocked_net'],
                        ]
        self.default_tip = _("Place mouse on any computer to see brief info about it.\n\
You can select and unselect multiple host clicking on every one.\n\
Drag and drop hosts to positions and save clicking on right mouse button.")
        
        
        self.icon_tooltips = None
        
        self.classview=self.ui.get_widget('classview')
        self.classeventbox=self.ui.get_widget('classeventbox')
        self.classview.drag_dest_set(gtk.DEST_DEFAULT_MOTION |
                                  gtk.DEST_DEFAULT_HIGHLIGHT |
                                  gtk.DEST_DEFAULT_DROP,
                                  [], gtk.gdk.ACTION_MOVE)
        self.classview.drag_dest_set(0, [], 0)
        self.classview.connect('drag_motion', self.motion_cb)
        self.classview.connect('drag_drop', self.on_drag_data_received)
        self.classeventbox.connect("button_press_event", self.on_classview_click)
        #self.classeventbox.connect("size-allocate", self.get_max_pos)
        self.classeventbox.connect("motion-notify-event", self.on_classview_event)
        
        self.oldpos={}
        #self.classview.set_size_request(200, 200)
        self.initialX=10
        self.initialY=10
        self.position=[10,10]
        self.iconsize=[115,115]
        
        # gtk.Frame don't support changing background color (default gray) use glade eventbox
        self.classeventbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
        self.loadpos()

    def get_max_pos(self, *args):
        x, y, width, height = self.classeventbox.get_allocation()
        #print_debug("get_max_pos() width=%s height=%s"%(width, height))
        return [width, height]


    def isenabled(self):
        """
        return True if only configuration enable IconView
        prevent to work if ClassView is hidden
        """
        if self.main.config.GetVar("listmode") == 'icons' or \
             self.main.config.GetVar("listmode") == 'both' or \
             self.main.config.GetVar("listmode") == 'class':
            return True
        return False

    def isactive(self):
        """
        Return True if IconView is enabled and is active (We click on it)
        know this getting tabindex of viewtabas widget.
          0 => active list view
          1 => active icon view
        """
        if not self.isenabled:
            return False
        if self.main.viewtabs.get_current_page() != 2:
            return False
        #print_debug("isactive() ClassView Mode active")
        return True

    def set_selected(self, ip):
        self.__selected_icon=ip

    def get_selected(self):
        return self.__selected_icon

    def get_host(self, ip):
        if self.hosts.has_key(ip):
            return self.hosts[ip]['hostname']

    def __increment_position(self):
        maxpos=self.get_max_pos()
        #print_debug("__increment_position() self.position[0](%s) >= maxpos[0](%s) -self.iconsize[0](%s)"%(self.position[0], maxpos[0], self.iconsize[0]))
        if self.position[0] + self.iconsize[0] >= maxpos[0] - self.iconsize[0]:
            #print_debug("__increment_position() NEW FILE")
            self.position[1]=self.position[1]+self.iconsize[1]
            self.position[0]=self.initialX
        else:
            self.position[0]=self.position[0]+self.iconsize[0]
        print_debug("__increment_position()  position=%s"%(self.position))

    def __getoverride(self, ax, ay, aip):
        # read oldpos to know override saved settings
        for h in self.oldpos:
            if h == aip:
                # self movement
                continue
            x, y = self.oldpos[h]
            diffx=abs(ax-x) - (self.iconsize[0]-5)
            diffy=abs(ay-y) - (self.iconsize[1]-20)
            if diffx < 0 and diffy < 0:
                #print_debug("__getoverride() h=%s self.oldpos[h]=%s => [%s,%s] diffx=%s diffy=%s"%(h, self.oldpos[h], ax, ay, diffx, diffy))
                return True
        # read pos of printed icons
        for w in self.classview.get_children():
            x, y, width, height = w.get_allocation()
            ip=[]
            for c in w.get_children():
                c.get_model().foreach(lambda model, path, iter: ip.append(model.get_value(iter, 1)) )
            if aip == ip[0]:
                # self movement
                continue
            diffx=abs(ax-x) - (self.iconsize[0]-5)
            diffy=abs(ay-y) - (self.iconsize[1]-20)
            #print_debug("__getoverride() ### POSITION ### Elem[%s,%s] new[%s,%s] => abs(ax-x)=%s abs(ay-y)=%s restax=%s restay=%s"%(x,y,ax,ay,abs(ax-x), abs(ay-y), diffx, diffy ))
            if diffx < 0 and diffy < 0:
                print_debug("__getoverride() ### POSITION ### Elem[%s,%s] new[%s,%s] => abs(ax-x)=%s abs(ay-y)=%s restax=%s restay=%s"%(x, y, ax, ay, abs(ax-x), abs(ay-y), diffx, diffy ))
                return True
        return False

    def savepos(self, widget, action):
        if action == "reset":
            self.oldpos={}
            self.main.config.SetVar("positions", "")
            self.main.config.SaveToFile()
            print_debug("savepos() reset to %s"%self.oldpos)
            self.main.write_into_statusbar( _("Positions reset to defaults.") )
            return
        for w in self.classview.get_children():
            x, y, width, height = w.get_allocation()
            ip=[]
            for c in w.get_children():
                c.get_model().foreach(lambda model, path, iter: ip.append(model.get_value(iter, 1)) )
            print_debug("savepos() ### POSITION ### x=%s y=%s width=%s height=%s ip=%s"%(x, y, width, height, ip))
            self.oldpos[ip[0]]=[x,y]
        print_debug("savepos() self.oldpos=%s"%self.oldpos)
        txt=""
        for ip in self.oldpos:
            txt+="%s:%s:%s,"%(ip, self.oldpos[ip][0], self.oldpos[ip][1] )
        # remove last coma
        txt=txt[:-1]
        print_debug("savepos() txt=%s"%txt)
        self.main.config.SetVar("positions", txt)
        self.main.config.SaveToFile()
        self.main.write_into_statusbar( _("Positions saved.") )

    def loadpos(self):
        print_debug("loadpos()")
        txt=self.main.config.GetVar("positions")
        if txt == "": return
        self.oldpos={}
        a=txt.split(',')
        for host in a:
            if len(host) < 1: continue
            h=host.split(':')
            self.oldpos[h[0]]=[int(h[1]),int(h[2])]
        print_debug("loadpos() self.oldpos=%s"%self.oldpos)

    def clear(self):
        for w in self.classview.get_children():
            w.destroy()
        self.position=[self.initialX,self.initialY]
        print_debug("clear() restore position to %s"%(self.position))
        self.selected=[]


    def generate_icon(self, data):
        print_debug("generate_icon() ip=%s hostname=%s"%(data['ip'], data['hostname']) )
        
        iconview=gtk.IconView()
        model = gtk.ListStore(str, str, gtk.gdk.Pixbuf)
        if data['username'] == shared.NO_LOGIN_MSG and not data['standalone']:
            pixbuf = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + shared.icon_image_no_logged)
        elif data['standalone']:
            pixbuf = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + shared.icon_image_standalone)
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + shared.icon_image_thin)
        
        if not data['active']:
            pixbuf.saturate_and_pixelate(pixbuf, 0.6, True)
        
        if data['image_blocked']:
            pixbuf2 = data['image_blocked']
            print("generate_icon() compositing isblocked=True")
            pixbuf2.composite(pixbuf, 0, 0, pixbuf.props.width, pixbuf.props.height, 0, 0, 1.0, 1.0, gtk.gdk.INTERP_HYPER, 255)
        
        iconview.set_model(model)
        iconview.set_text_column(0)
        iconview.set_pixbuf_column(2)
        if hasattr(iconview.props, 'has_tooltip'):
            iconview.props.has_tooltip = True
        
        #if data['username'] == shared.NO_LOGIN_MSG:
        #    model.append([data['username'], data['ip'], pixbuf])
        model.append([data['username'], data['ip'], pixbuf])
        
        iconview.show()
        # in old versions of gtk we need to put explicity iconview size
	if gtk.gtk_version < (2,10,0):
            iconview.set_size_request(pixbuf.props.width+14, pixbuf.props.height+28)
        
        # connect drag and drop signal with external data
        iconview.drag_dest_set( gtk.DEST_DEFAULT_ALL, [( 'text/uri-list', 0, 2 ), ], gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_COPY)
        iconview.connect( 'drag_data_received', self.on_external_drag_data_received, data['ip'])

        #iconview.set_size_request(110,110)
        iconview.set_item_width(82)
        button = gtk.Button()
        button.set_relief(gtk.RELIEF_NONE)
        button.add(iconview)


        button.drag_source_set(gtk.gdk.BUTTON1_MASK, [], gtk.gdk.ACTION_COPY)
        if data['active']:
            button.connect("button_press_event", self.on_iconview_click, data['ip'])
        button.connect("enter", self.on_button_enter, data['ip'])
        button.set_size_request(111,113)
        button.show_all()
        
        if self.oldpos.has_key(data['ip']):
            # we have and old possition
            print_debug("generate_icon() found old position => %s"%self.oldpos[data['ip']])
            self.classview.put(button, self.oldpos[data['ip']][0], self.oldpos[data['ip']][1] )
        else:
            #while self.__getoverride(self.position[0], self.position[1], data['ip'] ):
            #    print_debug("generate_icon() OVERRIDE ICON !!!")
            #    self.__increment_position()
            self.classview.put(button, self.position[0], self.position[1])
            print_debug("generate_icon() put not positioned icon at [%s,%s] !!!"%(self.position[0], self.position[1]))
            self.__increment_position()
            
        self.hosts[data['ip']]=data

    def on_external_drag_data_received( self, widget, context, x, y, selection, targetType, dtime, ip_recv):
        ip=None
        if not self.ismultiple():
            if not ip_recv: return
            ip=ip_recv
            self.set_selected(ip)
        print_debug("get_selected()=%s get_multiple()=%s" %(self.get_selected(), self.get_multiple()))
        filenames=[]
        files = selection.data.split('\n')
        extensions = (".avi", ".mpg", ".mpeg", ".ogg", ".ogm", ".asf", ".divx", 
                    ".wmv", ".vob", ".m2v", ".m4v", ".mp2", ".mp4", ".ac3", 
                    ".ogg", ".mp1", ".mp2", ".mp3", ".wav", ".wma")
        print_debug("on_external_drag_data_received() files=%s dtime=%s ip=%s"%(files, dtime, ip))
        for f in files:
            if f:
                filenames.append(f.strip().replace('%20', ' '))
                #break
        if len(filenames) < 1:
            return
        
        if filenames[0].startswith('file:///') and filenames[0].lower().endswith('.desktop') and os.path.isfile(filenames[0][7:]):
            if self.class_external_exe != None:
                self.class_external_exe(filenames[0][7:])
                print_debug("get_selected() ip=%s file=%s" %(self.get_selected(), filenames[0][7:]))
        elif filenames[0].startswith('file:///') and filter(filenames[0].lower().endswith, extensions) and os.path.isfile(filenames[0][7:]):
            if self.class_external_video != None:
                self.class_external_video(filenames[0][7:])
                print_debug("get_selected() ip=%s file=%s" %(self.get_selected(), filenames[0][7:]))
        elif filenames[0].startswith('file:///') and os.path.isfile(filenames[0][7:]):
            if self.class_external_send != None:
                self.class_external_send(filenames)
                print_debug("get_selected() ip=%s file=%s" %(self.get_selected(), filenames))
        else:
            shared.error_msg( _("%s is not a valid file to exe or send") %(os.path.basename(filenames[0][7:])) )
        return True

    def on_drag_data_received(self, widget, context, x, y, dtime):
        button=context.get_source_widget()
        if not button:
            #print context
            #print dir(context)
            #print context.get_data()
            #print context.targets
            print_debug("on_drag_data_received() no button detected")
            return
        bx, by, width, height = button.get_allocation()
        # calculate newx and newy with valid positions
        newx=x-(width/2)
        newy=y-(height/2)
        maxpos=self.get_max_pos()
        if newx < 0: newx=10
        if newy < 0: newy=10
        print_debug("on_drag_data_received() newx=%s newy=%s maxpos[0]=%s maxpos[1]=%s"%(newx, newy, maxpos[0], maxpos[1]))
        if newx > maxpos[0]:
            print_debug("on_drag_data_received() newx=%s > maxpos[0]=%s or negative"%(newx, maxpos[0]))
            return
        if newy > maxpos[1]:
            print_debug("on_drag_data_received() newy=%s > maxpos[1]=%s or negative"%(newy, maxpos[1]))
            return
        # get button ip address and pass to __getoverride to not put 2 hosts (with different IP) in same position
        ip=[]
        for c in button.get_children():
            c.get_model().foreach(lambda model, path, iter: ip.append(model.get_value(iter, 1)) )
        if self.hosts[ip[0]]['active']:
            # set unselect if host is active
            self.change_select(c, ip[0])
        #if self.__getoverride(newx, newy, ip[0]):
        #    print_debug("on_drag_data_received() ip=%s another host is near x=%s y=%s, don't move!!"%(ip[0], x, y) )
        #    self.main.write_into_statusbar( _("Can't move icon, another host is near.") )
        #    return
        self.classview.move(button, newx, newy)

    def motion_cb(self, widget, context, x, y, time):
        context.drag_status(gtk.gdk.ACTION_MOVE, time)
        return True

    def change_select(self, widget, ip):
        #print_debug("change_colour() ip=%s widget=%s"%(ip,widget))
        colour_selected=gtk.gdk.color_parse("#98ec98") # green
        colour_white=gtk.gdk.color_parse("white")
        style = widget.get_style().copy()
        
        if self.isselected(ip):
            style.base[gtk.STATE_NORMAL] = colour_white
            style.base[gtk.STATE_PRELIGHT] = colour_white
            self.set_unselect(ip)
        else:
            style.base[gtk.STATE_NORMAL] = colour_selected
            style.base[gtk.STATE_PRELIGHT] = colour_selected
            self.set_select(ip)
        widget.set_style(style)

    def on_iconview_click(self, widget, event, ip):
        if event.button == 3:
            # right click show menu
            print_debug("on_iconview_click() ip=%s" %(ip))
            self.main.menus.RightClickMenuOne( None , None, ip)
            self.main.menu.popup( None, None, None, event.button, event.time)
            #self.set_select(ip)
            self.set_selected(ip)
            return True
        if event.button == 1:
            # select host (change color) and call set_selected or set_unselected
            for c in widget.get_children():
                self.change_select(c, ip)

    def on_classview_click(self, iv, event):
        if event.button == 3:
            # need to remake allmenu (for title selected|all )
            #print_debug( "on_classview_click() all=%s"%self.selected )
            self.main.menus.RightClickMenuAll()
            self.main.allmenu.popup( None, None, None, event.button, event.time)
            return

    def on_button_enter(self, button, ip):
        txt=""
        data=self.hosts[ip]
        for info in self.avalaible_info:
            if data[info[1]] == True:
                value=_("yes")
            elif data[info[1]] == False:
                value=_("no")
            else:
                value=data[info[1]]
            txt+=" %s: %s \n" %(info[0], value)
        self.icon_tooltips = gtk.Tooltips()
        self.icon_tooltips.set_tip(button, txt)

    def get_multiple(self):
        return self.selected

    def set_select(self, ip):
        print_debug("set_select() ip=%s all=%s"%(ip, self.selected))
        if ip in self.selected:
            return
        self.selected.append(ip)

    def set_unselect(self, ip):
        if self.isselected(ip):
            self.selected.remove(ip)
        print_debug("set_unselect() ip=%s all=%s"%(ip, self.selected))

    def isselected(self, ip):
        if ip in self.selected:
            #print_debug("isselected() TRUE ip=%s"%ip)
            return True
        #print_debug("isselected() FALSE ip=%s"%ip)
        return False

    def ismultiple(self):
        if not self.isactive():
            return False
        print_debug("ismultiple() self.selected=%s"%self.selected)
        if len(self.selected) > 0:
            return True
        else:
            return False

    def on_classview_event(self, widget, event):
        if not event.state:
            #print_debug("on_classview_event() tip")
            self.icon_tooltips = gtk.Tooltips()
            self.icon_tooltips.set_tip(widget, self.default_tip)


    def change_lockscreen(self, ip, pixbuf2, status_screen, status_net):
        print_debug("change_lockscreen() ip=%s pixbuf=%s"%(ip, pixbuf2))
        self.hosts[ip]['blocked_screen']=status_screen
        self.hosts[ip]['blocked_net']=status_net
        data=self.hosts[ip]
        if data['username'] == shared.NO_LOGIN_MSG:
            pixbuf = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + shared.icon_image_no_logged)
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(shared.IMG_DIR + shared.icon_image_thin)
        pixbuf2.composite(pixbuf, 0, 0, pixbuf.props.width, pixbuf.props.height, 0, 0, 1.0, 1.0, gtk.gdk.INTERP_HYPER, 255)
        for w in self.classview.get_children():
            for c in w.get_children():
                model=c.get_model()
                if model[0][1] == ip:
                    model2 = gtk.ListStore(str, str, gtk.gdk.Pixbuf)
                    c.set_model(model2)
                    c.set_text_column(0)
                    c.set_pixbuf_column(2)
                    if data['username'] == shared.NO_LOGIN_MSG:
                        model2.append([data['hostname'].replace('.aula',''), data['ip'], pixbuf])
                    else:
                        model2.append([data['username'], data['ip'], pixbuf])
                    #model[0][2]=pixbuf
                    return



