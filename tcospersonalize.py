#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##########################################################################
# TcosPersonalize writen by MarioDebian <mariodebian@gmail.com>
#
#    TcosPersonalize version __VERSION__
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

import sys
import os
import glob

if not os.path.isfile("Initialize.py"):
        #print "DEBUG: append tcosmonitor dir"
        sys.path.append("/usr/share/tcosmonitor")


import pygtk
pygtk.require('2.0')
from gtk import *
import gtk.glade

from time import time, sleep
import getopt
from gettext import gettext as _
from subprocess import Popen, PIPE, STDOUT

import gobject

if not os.path.isfile("shared.py"):
        sys.path.append('/usr/share/tcosmonitor')
else:
        sys.path.append('./')
        
import shared
import pwd,grp


debug_name="tcospersonalize"

PXELINUX_CFG=[
    "default __TCOS_METHOD__",
    "prompt 0",
    "timeout 50",
    "label default",
    "  kernel vmlinuz-__TCOS_KERNEL__",
    "  append ramdisk_size=65536 boot=tcos root=/dev/ram0 initrd=initramfs-__TCOS_KERNEL__ __TCOS_CMDLINE__",
    "label nfs",
    "  kernel vmlinuz-__TCOS_KERNEL__",
    "  append ramdisk_size=32768 boot=tcos root=/dev/ram0 initrd=initramfs-__TCOS_KERNEL__-nfs forcenfs __TCOS_CMDLINE__",
    "",
    "#kernel=__TCOS_KERNEL__",
    "#method=__TCOS_METHOD__",
    "#cmdline='__TCOS_CMDLINE__'",
]

PXE_METHODS=[
"default",
"nfs"
]

PXELINUX_CMDLINE="quiet splash"

def print_debug(txt):
    if shared.debug:
        print "%s::%s" %(debug_name, txt)
    return

def crono(start, txt):
    print_debug ("crono(), %s get %f seconds" %(txt, (time() - float(start))) )
    return

def usage():
    print "TcosPersonalize help:"
    print ""
    print "   tcospersonalize [--host=XXX.XXX.XXX.XXX]   (host to personalize)"
    print "   tcospersonalize -d [--debug]  (write debug data to stdout)"
    print "   tcospersonalize -h [--help]   (this help)"


try:
    opts, args = getopt.getopt(sys.argv[1:], ":hd", ["help", "debug", "host="])
except getopt.error, msg:
    print msg
    print "for command line options use tcosconfig --help"
    sys.exit(2)

# process options
for o, a in opts:
    if o in ("-d", "--debug"):
        print "DEBUG ACTIVE"
        shared.debug = True
    if o == "--host":
        print "HOST %s" %(a)
        shared.remotehost = a
    if o in ("-h", "--help"):
        usage()
        sys.exit()


class TcosPersonalize:
    def __init__(self):
        print_debug ( "__init__()" )
        self.name="TcosPersonalize"
        # exit if no host
        if shared.remotehost == None:
            usage()
            shared.error_msg ( _("Need a host to configure!!!\nTry exec:\n tcospersonalize --host=XXX.XXX.XXX.XXX") )
            sys.exit(1)
        
        nogroup=True
        for group in os.getgroups():
            if grp.getgrgid(group)[0] == "tcos":
                nogroup=False
        
        if nogroup and os.getuid() != 0:
            shared.error_msg( "You must be root to exec tcospersonalize." )
            sys.exit(1)
        
        self.remotehost_config = os.path.join ("/var/lib/tcos/tftp/conf/", shared.remotehost + ".conf" )
        
        #import shared
        gtk.glade.bindtextdomain(shared.PACKAGE, shared.LOCALE_DIR)
        gtk.glade.textdomain(shared.PACKAGE)
        
        # Widgets
        print_debug("loading %s" %(shared.GLADE_DIR + 'tcospersonalize.glade'))
        self.ui = gtk.glade.XML(shared.GLADE_DIR + 'tcospersonalize.glade')
        self.main = self.ui.get_widget('mainwindow')

        # close windows signals
        self.main.connect('destroy', self.quitapp )
        
        # buttons
        self.buttonok=self.ui.get_widget('ok_button')
        self.buttoncancel=self.ui.get_widget('cancel_button')
        self.buttondelete=self.ui.get_widget('delete_button')
        self.buttongetavalaible=self.ui.get_widget('getavalaible_button')
        
        # signals on buttons
        self.buttonok.connect('clicked', self.on_buttonok_click )
        self.buttoncancel.connect('clicked', self.on_buttoncancel_click )
        self.buttondelete.connect('clicked', self.on_buttondelete_click )
        self.buttongetavalaible.connect('clicked', self.on_buttongetavalaible_click )
        
        # get combos
        self.combo_xsession=self.ui.get_widget('combo_xsession')
        self.combo_xdriver=self.ui.get_widget('combo_xdriver')
        self.combo_xres=self.ui.get_widget('combo_xres')
        self.combo_xdepth=self.ui.get_widget('combo_xdepth')
        
        # get checkboxes
        self.ck_xmousewheel=self.ui.get_widget('ck_xmousewheel')
        self.ck_xdontzap=self.ui.get_widget('ck_xdontzap')
        self.ck_xdpms=self.ui.get_widget('ck_xdpms')
        
        # get textboxes
        #self.text_extramodules=self.ui.get_widget('txt_extramodules')
        self.text_xhorizsync=self.ui.get_widget('txt_xhorizsync')
        self.text_xvertsync=self.ui.get_widget('txt_xvertsync')
        
        # boot options
        self.combo_kernel=self.ui.get_widget('combo_kernel')
        self.combo_method=self.ui.get_widget('combo_method')
        self.text_cmdline=self.ui.get_widget('txt_cmdline')
        self.buttonapply=self.ui.get_widget('apply_button')
        self.buttonapply.connect('clicked', self.on_buttonapply_click )
        
        self.deleteboot=self.ui.get_widget('delete_boot_button')
        self.deleteboot.connect('clicked', self.on_deleteboot_click )
        
        # host label
        self.hostlabel=self.ui.get_widget('label_host')
        self.hostlabel.set_markup ( "<b>" + _("host: ") + shared.remotehost + "</b>" )
        
        # get conf file
        self.vars=[]
        self.OpenFile()
        
        found=False
        for var in self.vars:
            if var[0] == "xdisablesync":
                found=True
        if not found:
            print_debug("adding xdisablesync....")
            self.vars.append(["xdisablesync", ""])
        
        # populate combos
        self.populate_select(self.combo_xsession, shared.xsession_values )
        self.set_active_in_select(self.combo_xsession, self.GetVar("xsession") )
        
        self.populate_select(self.combo_xdriver, shared.xdriver_values )
        self.set_active_in_select(self.combo_xdriver, self.GetVar("xdriver") )
        
        #self.populate_select(self.combo_xdriver, ['auto'] )
        #self.set_active_in_select(self.combo_xdriver, "\"auto\"" )
        
        self.populate_select(self.combo_xres, shared.xres_values )
        self.set_active_in_select(self.combo_xres, self.GetVar("xres")  )
        
        self.populate_select(self.combo_xdepth, shared.xdepth_values )
        self.set_active_in_select(self.combo_xdepth, self.GetVar("xdepth") )
        
        # populate checkbox
        #self.populate_checkboxes( self.ck_xmousewheel, 1)
        #self.populate_checkboxes( self.ck_xdontzap, 1)
        #self.populate_checkboxes( self.ck_xdpms, 1)
        
        self.populate_checkboxes( self.ck_xmousewheel, self.GetVar("xmousewheel") )
        self.populate_checkboxes( self.ck_xdontzap, self.GetVar("xdontzap") )
        self.populate_checkboxes( self.ck_xdpms, self.GetVar("xdpms") )
        
        self.populate_textboxes( self.text_xhorizsync, self.GetVar("xhorizsync") )
        self.populate_textboxes( self.text_xvertsync, self.GetVar("xvertsync") )
        
        kernels=self.getkernels()
        
        self.bootfilename=self.get_hexfilename(shared.remotehost)
        self.bootparams={'kernel':'', 'method':'default', 'cmdline':'quiet splash'}
        
        if os.path.isfile(self.bootfilename):
            f=open(self.bootfilename, 'r')
            for line in f.readlines():
                if line.startswith("#kernel"):
                    self.bootparams['kernel']=line.split('=')[1].strip()
                if line.startswith("#method"):
                    self.bootparams['method']=line.split('=')[1].strip()
                if line.startswith("#cmeline"):
                    self.bootparams['cmdline']=line.split('=')[1].strip()
            f.close()
            self.deleteboot.set_sensitive(True)
        else:
            if len(kernels) == 1:
                self.bootparams['kernel']=kernels[0]
            else:
                self.buttonapply.set_sensitive(False)
                self.combo_kernel.connect('changed', self.on_combo_kernel_change)
            self.deleteboot.set_sensitive(False)
        
        self.populate_select(self.combo_kernel, kernels )
        self.set_active_in_select(self.combo_kernel, self.bootparams['kernel']  )
            
        
        self.populate_select(self.combo_method, PXE_METHODS )
        self.set_active_in_select(self.combo_method, self.bootparams['method']  )
        self.text_cmdline.set_text(PXELINUX_CMDLINE)
        
        # populate textboxes
        # NOTHING
        
        self.issaved=False
        # end init process
        
    def CheckConfFile(self):
        self.isnew=False
        if not os.path.isfile(self.remotehost_config):
            print_debug ( "CheckConfFile() %s not exists" %(self.remotehost_config) )
            self.isnew=True
            self.CreateConfFile()
            
    def CreateConfFile(self):
        print_debug ( "CreateConfFile()" )
        # save this into file
        fd=file(self.remotehost_config, 'w')
        for item in shared.PersonalizeConfig:
            key=item[0]
            value=item[1]
            print_debug ("key=%s value=%s" %(key, value))
            fd.write("%s=\"%s\"\n" %(key, value) )
        fd.close
        self.FirstRunning=True
            
    def OpenFile(self):
        self.CheckConfFile()
        conf=None
        conf=[]
        print_debug("open_file() reading data from \"%s\"..."\
                                     %(self.remotehost_config) )
        fd=file(self.remotehost_config, 'r')
        self.data=fd.readlines()
        fd.close()
        for line in self.data:
            if line != '\n':
                line=line.replace('\n', '')
                conf.append(line)
        print_debug ( "OpenFile() Found %d vars" %( len(conf)) )
        if len(conf) <1:
            print_debug ( "OpenFile() FILE IS EMPTY!!!" )
            return
        for i in range( len(conf) ):
            if conf[i].find("#") != 0:
                #print_debug ( "OpenFile() conf=" + conf[i] )
                (var,value)=conf[i].split("=", 1)
                self.vars.append([var,value])

    def GetVar(self, varname):
        for i in range( len(self.vars) ):
            if self.vars[i][0].find(varname) == 0:
                print_debug ( "GetVar() found, %s=%s" \
                                %(self.vars[i][0], self.vars[i][1]) )
                return self.vars[i][1]
        print_debug ( "GetVar() not found, %s, returning \"\"" %(varname) )
        return ""
    
    def SetVar(self, varname, value):
        print_debug ( "SetVar(%s)=\"%s\"" %(varname, value) )
        for i in range(len(self.vars)):
            if varname == self.vars[i][0]:
                print_debug ( "changing %s value %s to \"%s\" of %s"\
                         %(self.vars[i][0], self.vars[i][1], value, varname) )
                self.vars[i][1]="\"%s\"" %(value)
    
    def SaveToFile(self):
        self.issaved=True
        print_debug ( "SaveToFile() len(self.vars)=%d" %( len(self.vars) ) )
        if len(self.vars) < 1:
            print_debug ( "SaveToFile() self.vars is empty" )
            return
        
        try:
            fd=file(self.remotehost_config, 'w')
        except IOError:
            shared.error_msg( "Can't write into %s file.\n\nRun as root?" %(self.remotehost_config) )
            return
        for i in range(len(self.vars)):
            fd.write("%s=%s\n" %(self.vars[i][0], self.vars[i][1]))
        fd.close
        print_debug ( "SaveToFile() new settings SAVED!!!")   
        return
    
    def SaveSettings(self):
        """
        save settings
        """
        print_debug ( "SaveSettings() INIT" )
        
        # read combos
        self.SetVar("xsession", self.read_select_value(self.combo_xsession, "xsession") )
        self.SetVar("xdriver", self.read_select_value(self.combo_xdriver, "xdriver") )
        self.SetVar("xres", self.read_select_value(self.combo_xres, "xres") )
        self.SetVar("xdepth", self.read_select_value(self.combo_xdepth, "xdepth") )
        
        self.SetVar("xhorizsync", self.read_textbox(self.text_xhorizsync, "xhorizsync"))
        self.SetVar("xvertsync", self.read_textbox(self.text_xvertsync, "xvertsync") )
        
        if self.GetVar("xhorizsync") == "\"disable\"" or self.GetVar("xvertsync") == "\"disable\"":
            self.SetVar("xdisablesync", "disable")
        else:
            self.SetVar("xdisablesync", "")
        
        # read checkboxes
        self.read_checkbox(self.ck_xmousewheel, "xmousewheel")
        self.read_checkbox(self.ck_xdontzap, "xdontzap")
        self.read_checkbox(self.ck_xdpms, "xdpms")
        
        # save to file
        self.SaveToFile()
    
    def populate_select(self, widget, values, set_text_column=True):
        valuelist = gtk.ListStore(str)
        for value in values:
            #print_debug ( "populate_select() appending %s" %([value.split('_')[0]]) ) 
            valuelist.append( [value.split('_')[0]] )
        widget.set_model(valuelist)
        if set_text_column:
            widget.set_text_column(0)
        model=widget.get_model()
        return
    
    def set_active_in_select(self, widget, default):
        model=widget.get_model()
        for i in range(len(model)):
            #print model[i][0] + default
            if "\"%s\"" %(model[i][0]) == default or model[i][0] == default:
                print_debug ("set_active_in_select(%s) default is %s, index %d"\
                                     %(widget.name, model[i][0] , i ) )
                widget.set_active(i)
                return
        print_debug ( "set_active_in_select(%s) NOT HAVE DEFAULT" %(widget.name) )  
    
    def populate_checkboxes(self, widget, value):
        if value == "\"1\"" or value == "1":
            value=1
        elif value== "\"0\"" or value == "0":
            value=0
        else:
            print_debug ( "populate_checkboxes() unknow value=\"%s\"" %(value) )
            return
        checked=int(value)
        if checked == 1:
            widget.set_active(1)
        else:
            widget.set_active(0)
        return

    def populate_textboxes(self, widget, value):
        if value:
            widget.set_text(value.replace('"','') )
        
    def read_select_value(self, widget, varname):
        selected=-1
        try:
            selected=widget.get_active()
        except Exception, err:
            print_debug ( "read_select() ERROR reading %s, error=%s" %(varname,err) )
        model=widget.get_model()
        value=model[selected][0]
        print_debug ( "read_select() reading %s=%s" %(varname, value) )
        return value
    
    def read_checkbox(self, widget, varname):
        if widget.get_active() == 1:
            print_debug ( "read_checkbox(%s) CHECKED" %(widget.name) )
            self.SetVar(varname, 1)
        else:
            print_debug ( "read_checkbox(%s) UNCHECKED" %(widget.name) )
            self.SetVar(varname, 0)
            
    def read_textbox(self, widget, varname):
        print widget.get_text()
        if widget.get_text():
            print_debug ( "read_textbox(%s) value=%s" %(widget.name, widget.get_text() ) )
            return widget.get_text()
        else:
            print_debug ( "read_textbox(%s) can't read textbox" %(widget.name) )
            return ""
        
    def on_buttongetavalaible_click(self, widget):
        print_debug( "on_button_getavalaible_click()" )
        import TcosXauth
        self.xauth=TcosXauth.TcosXauth(self)
        import TcosConf
        self.config=TcosConf.TcosConf(self)
        import TcosXmlRpc
        self.xmlrpc=TcosXmlRpc.TcosXmlRpc(self)
        self.xmlrpc.newhost(shared.remotehost)
        if not self.xmlrpc.connected:
            shared.error_msg ( _("Host down, can't connect to tcosxmlrpc.") )
            print_debug ( "on_buttongetavalaible_click() host down!!" )
            return
        #alldrivers=self.xmlrpc.GetDevicesInfo("", "--getxdrivers").split('|')[0:-1]
        alldrivers=self.xmlrpc.GetDevicesInfo("", "--getxdrivers")
        print_debug ( "on_buttongetavalaible_click() alldrivers=%s" %(alldrivers) )
        alldrivers=alldrivers.split('|')[0:-1]
        self.populate_select(self.combo_xdriver, shared.xdriver_values + alldrivers, set_text_column=False)
        shared.info_msg ( _("New %d drivers loaded from terminal.") %(len(alldrivers)) )
    
    def on_buttonok_click(self, widget):
        print_debug ( "on_buttonok_click()" )
        self.SaveSettings()
        self.quitapp()

    def on_combo_kernel_change(self, widget):
        if self.read_select_value(widget, 'kernel') != '':
            self.buttonapply.set_sensitive(True)
    
    def get_hexfilename(self, ip):
        name=""
        for a in ip.split('.'):
            hexn="%X" %int(a)
            if len(hexn) == 1:
                hexn="0%s"%hexn
            name="%s%s"%(name, hexn )
        return os.path.join("/var/lib/tcos/tftp/pxelinux.cfg" , name )
    
    def on_buttonapply_click(self, widget):
        print_debug("on_buttonapply_click()")
        kernel=self.read_select_value(self.combo_kernel, 'kernel')
        method=self.read_select_value(self.combo_method, 'method')
        cmdline=self.text_cmdline.get_text()
        
        try:
            f=open(self.bootfilename, 'w')
        except Exception, err:
            print_debug("Error opening %s, error=%s"%(filename,err) )
            return
        
        for line in PXELINUX_CFG:
            out=line.replace('__TCOS_KERNEL__', kernel)
            out=out.replace('__TCOS_METHOD__', method)
            out=out.replace('__TCOS_CMDLINE__', cmdline)
            f.write(out + '\n')
        f.close()
        self.deleteboot.set_sensitive(True)
    
    def on_deleteboot_click(self, widget):
        print_debug("on_deleteboot_click() ")
        try:
            os.unlink(self.bootfilename)
            self.deleteboot.set_sensitive(False)
        except Exception, err:
            print_debug("on_deleteboot_click() Exception deleting: %s"%err)
    
    def on_buttoncancel_click(self, widget):
        print_debug ( "on_buttoncancel_click()" )
        if not self.issaved and self.isnew:
            # delete file
            print_debug ( "on_buttoncancel_click() deleting file" )
            os.remove(self.remotehost_config)
        self.quitapp()    

    def on_buttondelete_click(self, widget):
        print_debug ( "on_buttondelete_click()" )
        # ask for delete
        if shared.ask_msg ( _("Really delete config of %s?") %(shared.remotehost) ):
            print_debug ( "on_buttondelete_click() deleting file" )
            os.remove(self.remotehost_config)
        shared.info_msg ( _("Deleted!") )
        self.quitapp()

    def getkernels(self):
        # valid kernel >= 2.6.12
        # perpahps we can try to build initrd image instead of initramfs
        # in kernel < 2.6.12, this require a lot of work in gentcos and init scripts
        kernels=[]
        #print_debug ("getkernels() read all vmlinuz in /boot/")
        #for _file in os.listdir(shared.chroot + '/boot'):
        # FIXME need to detect chroot kernels
        #for _file in os.listdir('/var/lib/tcos/tftp'):
        for _file in glob.glob('/var/lib/tcos/tftp/vmlinuz*'):
            try:
                os.stat(_file)
            except Exception, err:
                print_debug("getkernels() link %s broken, error=%s" %(_file,err) )
                continue
            kernel=os.path.basename(_file).replace('vmlinuz-','')
            print_debug("getkernels() found %s"%kernel)
            # split only 3 times
            try:
                (kmay, kmed, kmin) = kernel.split('.',2)
            except Exception, err:
                print_debug("getkernels() exception spliting kernel '%s' version, %s"%(kernel,err))
                continue
            import re
            pattern = re.compile ('[-_.+]')
            (kmin, kextra) = pattern.split(kmin,1)
            # need kernel >= 2.6.12
            if int(kmay)==2 and int(kmed)==6 and int(kmin)>=12:
                #print_debug( "getkernels() VALID kernel %s" %(kernel) )
                kernels.append(kernel)
            else:
                print_debug( "getkernels() INVALID OLD kernel %s" %(kernel) )
        return kernels

    def quitapp(self,*args):
        print_debug ( _("Exiting") )
        gtk.main_quit()

    def run (self):
        try:
            gtk.main()
        except KeyboardInterrupt:
            self.quitapp()


if __name__ == '__main__':
    #gtk.gdk.threads_init()
    gobject.threads_init()
    app = TcosPersonalize ()
    # Run app
    app.run ()
