#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##########################################################################
# TcosMonitor writen by MarioDebian <mariodebian@gmail.com>
#
#    tcos-devices version 0.0.15
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

import os, sys
import gobject
import getopt
from gettext import gettext as _
import time
import socket


if not os.path.isfile("shared.py"):
        sys.path.append('/usr/share/tcosmonitor')
else:
        sys.path.append('./')
        
import shared
# load conf file and exit if not active
if not shared.test_start("tcos-devices-ng") :
    print "tcos-devices-ng disabled at %s" %(shared.module_conf_file)
    sys.exit(1)
    
from TcosTrayIcon import *
import threading

import pygtk
pygtk.require('2.0')
from gtk import *
import gtk.glade
import pynotify
import pwd

# tell gtk we use threads
gtk.gdk.threads_init()



def usage():
    print "tcos-devices help:"
    print ""
    print "   tcos-devices [--host=XXX.XXX.XXX.XXX] "
    print "                 (force host to connect to reach devices, default is DISPLAY)"
    print "   tcos-devices --daemon      (run as daemon to scan dmesg output)"
    print "   tcos-devices -d [--debug]  (write debug data to stdout)"
    print "   tcos-devices -h [--help]   (this help)"

try:
    opts, args = getopt.getopt(sys.argv[1:], ":hd", ["help", "debug", "host=", ])
except getopt.error, msg:
    print msg
    print "for command line options use tcos-devices --help"
    sys.exit(2)

shared.remotehost, display =  os.environ["DISPLAY"].split(':')
action = ""

if len(display.split('.')) == 4:
    try:
        # we have an ip
        shared.remotehost=socket.gethostbyaddr(shared.remotehost)[0]
    except:
        pass

# process options
for o, a in opts:
    if o in ("-d", "--debug"):
        shared.debug = True
    if o == "--host":
        shared.remotehost = a
    if o in ("-h", "--help"):
        usage()
        sys.exit()

if shared.remotehost == "":
    print "tcos-devices: Not allowed to run in local DISPLAY"
    sys.exit(0)





def log( message ):
    print ( "%d %s" % (os.getpid(), message) )
    
def print_debug(txt):
    if shared.debug:
        print "%d %s::%s" %(os.getpid(), "tcos-devices-ng", txt)

def get_username():
    return pwd.getpwuid(os.getuid())[0]



class TcosDevicesNG:
    def __init__(self):
        self.host=shared.remotehost
        self.name="TcosDevicesNG"
        self.mounted={}
        self.username=get_username()
        
        self.systray=TcosTrayIcon()
        self.systray.status=True
        
        self.initremote()
        self.desktop=self.get_desktop()
        self.getremote_cdroms()
        self.getremote_floppy()
        
        self.quitting=False
        
        # register quit event
        self.systray.register_action("quit", lambda w: self.exit() )

        
        # start udev_daemon in new thread
        #self.udev_daemon=TcosUdev(self)
        #self.udev_daemon.start()
        
        #self.worker_running=False
        #self.worker=shared.Workers(self, target=self.udev_daemon, args=[])
        #self.worker.start()
        
        #self.udev_daemon()
        
        self.udev_events={ 
        "insert":       {"ID_BUS":  "usb",         "ACTION":"add"}, 
        "remove":       {"ID_BUS":  "usb",         "ACTION":"remove"},
        "mount-floppy": {"DEVPATH": "/block/fd0",  "ACTION":"mount"},
        "umount-floppy":{"DEVPATH": "/block/fd0",  "ACTION":"umount"},
        "mount-cdrom":  {"DEVPATH": "/block/hd*",   "ACTION":"mount"},
        "umount-cdrom": {"DEVPATH": "/block/hd*",   "ACTION":"umount"}, 
        "mount-flash":  {"DEVPATH": "/block/sd*",   "ACTION":"mount"},
        "umount-flash": {"DEVPATH": "/block/sd*",   "ACTION":"umount"}
        }
    
    def show_notification(self, msg, urgency=pynotify.URGENCY_CRITICAL):
        #print args
        #msg=args[0][0]
        #if len(args[0])< 2:
        #    urgency=pynotify.URGENCY_CRITICAL
        #else:
        #    urgency=args[1]
        pynotify.init("Multi Action Test")
        n = pynotify.Notification( _("Tcos device daemon") , msg )
        n.set_urgency(urgency)
        n.set_category("device")
        n.set_timeout(15000) # 15 sec
        if not n.show():
            print_debug  ("show_notification() Failed to send notification")
        
  
    def initremote(self):
        # get all devices
        import TcosXmlRpc
        import TcosConf
        import TcosXauth
        self.xauth=TcosXauth.TcosXauth(self)
        self.xauth.init_standalone()
        print_debug ( "loading config class..." )
        self.config=TcosConf.TcosConf(self, openfile=False)
        self.xmlrpc=TcosXmlRpc.TcosXmlRpc(self)
        
        # make a test and exit if no cookie match
        if not self.xauth.test_auth():
            print "tcos-devices: ERROR: Xauth cookie don't match"
            sys.exit(1)
        
        self.xmlrpc.newhost(self.host)
        if not self.xmlrpc.connected:
            print _("Error connecting with TcosXmlRpc in %s.") %(self.host)
            sys.exit(1)


    def getremote_cdroms(self):
        self.cdrom_devices=self.xmlrpc.GetDevicesInfo(device="", mode="--getcdrom").split('|')
        self.cdrom_devices=self.cdrom_devices[0:-1]
        print_debug ( "get_data() cdroms=%s" %(self.cdrom_devices) )
        for cdrom in self.cdrom_devices:
            # get device status
            cdrom_status= self.xmlrpc.GetDevicesInfo(device="/dev/%s" %cdrom, mode="--getstatus").replace('\n','')
            if cdrom_status == "0":
                mount=True
                umount=False
            else:
                mount=False
                umount=True
            self.systray.register_device("cdrom_%s"%cdrom, 
                            _("Cdrom device %s" %cdrom), 
                            "cdrom_mount.png", True, 
                            {
                        "cdrom_%s_mount" %cdrom: [ _("Mount Cdrom"),  "cdrom_mount.png", mount,  None, "/dev/%s"%cdrom],
                        "cdrom_%s_umount"%cdrom: [ _("Umount Cdrom"), "cdrom_umount.png", umount, None, "/dev/%s"%cdrom]
                            }, 
                            "/dev/%s"%(cdrom))
            self.systray.register_action("cdrom_%s_mount" %cdrom, self.cdrom, "mount", cdrom )
            self.systray.register_action("cdrom_%s_umount" %cdrom, self.cdrom, "umount", cdrom )

    def getremote_floppy(self):
        have_floppy=self.xmlrpc.GetDevicesInfo(device="/dev/fd0", mode="--exists").replace('\n','')
        if have_floppy == "0":
            print_debug ( _("No floppy detected") )
            return
        floppy_status=self.xmlrpc.GetDevicesInfo(device="/dev/fd0", mode="--getstatus").replace('\n','')
        if floppy_status == "0":
            mount=True
            n=1
            self.systray.status=False
        else:
            mount=False
            n=2
            self.systray.status=True
        self.systray.register_device("floppy", 
                            _("Floppy"), 
                            "floppy%s.png"%n, True, 
                            {
                        "floppy_mount": [ _("Mount Floppy"),  "floppy_mount.png", mount,  None, "/dev/fd0"],
                        "floppy_umount": [ _("Umount Floppy"), "floppy_umount.png", not mount, None, "/dev/fd0"]
                            }, 
                            "/dev/fd0")
        self.systray.register_action("floppy_mount" , self.floppy, "mount" )
        self.systray.register_action("floppy_umount" , self.floppy, "umount" )
        return

    def update_floppy(self, *args):
        if len(args) > 0:
            if args[0] == "mount":
                self.show_notification (  _("Floppy mounted. Ready for use.")  )
            elif args[0] == "umount":
                self.show_notification (  _("Floppy umounted. You can extract it.")  )
        floppy_status=self.xmlrpc.GetDevicesInfo(device="/dev/fd0", mode="--getstatus").replace('\n','')
        if floppy_status == "0":
            ismounted=False
            n=1
        else:
            ismounted=True
            n=2
        print_debug ("update_floppy() floppy ismounted=%s" %ismounted)
        self.systray.items["floppy"][1]="floppy%s.png"%n
        self.systray.update_status("floppy", "floppy_mount", not ismounted)
        self.systray.update_status("floppy", "floppy_umount", ismounted)

    def update_cdrom(self, *args):
        if len(args) > 0:
            if args[0] == "mount":
                self.show_notification (  _("Cdrom mounted. Ready for use.")  )
                return
            elif args[0] == "umount":
                self.show_notification (  _("Cdrom umounted. You can extract it.")  )
                return
            else:
                dev=args[0]
        cdrom_status=self.xmlrpc.GetDevicesInfo(device="/dev/%s"%dev, mode="--getstatus").replace('\n','')
        if cdrom_status == "0":
            ismounted=False
            n=1
        else:
            ismounted=True
            n=2
        print_debug ("update_cdrom() cdrom ismounted=%s" %ismounted)
        self.systray.update_status("cdrom_%s"%dev, "cdrom_%s_mount"%dev, not ismounted)
        self.systray.update_status("cdrom_%s"%dev, "cdrom_%s_umount"%dev, ismounted)


    def udev_daemon_start(self):
        while True:
            try:
                self.udev_daemon()
                time.sleep(3)
            except:
                log ("EE: udev_daemon Unexpected error: %s" %sys.exc_info()[0] )
                pass

    def udev_daemon(self):
        start1=time.time()
        print_debug ("udev_daemon() starting...")
        udev=self.xmlrpc.GetDevicesInfo(device="", mode="--getudev").split('|')
        print_debug("udev_daemon GetDevicesInfo time=%f" %(time.time() - start1) )
        if "error" in " ".join(udev): return
        udev=udev[:-1]
        if udev[0] == "unknow": return
        udev=self.remove_dupes(udev)
        for line in udev:
            data={}
            tmp=line.split('#')
            for i in tmp:
                if i:
                    data[i.split("=")[0]]=i.split("=")[1]
            for event in self.udev_events:
                action_found=False
                #print_debug ( " UDEV=> checking for event %s" %event )
                # check for all events
                for udev_var in self.udev_events[event]:
                    #print_debug ( "  UDEV=> checking for udev_var %s value=%s" %(udev_var, self.udev_events[event]["%s"%udev_var]) )
                    if not data.has_key(udev_var):
                        action_found=False
                        break
                    
                    if "*" in self.udev_events["%s"%event]["%s"%udev_var]:
                        even=self.udev_events["%s"%event]["%s"%udev_var].replace('*','')
                        if even in data["%s"%udev_var]:
                            action_found=True
                        else:
                            action_found=False
                            break
                    else:
                        if self.udev_events["%s"%event]["%s"%udev_var] == data["%s"%udev_var]:
                            action_found=True
                        else:
                            action_found=False
                            break
                    
                if action_found:
                    self.worker_running=False
                    worker=shared.Workers(self, target=self.do_udev_event, args=[data], dog=False)
                    worker.start() 
        
        print_debug("end of udev_daemon time=%f" %(time.time() - start1) )
        return            

        
    def do_udev_event(self, *args):
        data=args[0]
        print_debug ("do_udev_event() data=%s" %data)
        if data.has_key("ID_BUS") and data["ID_BUS"] == "usb":
            self.usb(data)
        
        if data.has_key("DEVPATH") and "/block/hd" in data["DEVPATH"]:
            self.update_cdrom(data["ACTION"])
            
        if data.has_key("DEVPATH") and "/block/fd" in data["DEVPATH"]:
            self.update_floppy(data["ACTION"])
        
        if data.has_key("DEVPATH") and "/block/sd" in data["DEVPATH"]:
            self.update_usb(data)


    def mounter_remote(self, device, fstype, mode="--mount"):
        print_debug ( "mounter_remote() device=%s fstype=%s" %(device, fstype) )
        if device == None:
            return False
        mnt_point="/mnt/%s" %(device[5:])
        if mode == "--mount":
            print_debug ( "mount_remote() mounting device=%s fstype=%s mnt_point=%s" %(device, fstype, mnt_point) )
        elif mode == "--umount":
            print_debug ( "mount_remote() umounting device=%s fstype=%s mnt_point=%s" %(device, fstype, mnt_point) )
        
        # set socket timeout bigger (floppy can take some time)
        import socket
        socket.setdefaulttimeout(15)
        
        mount=self.xmlrpc.GetDevicesInfo(device=device, mode=mode)
        if mount != mnt_point:
            print_debug ( "mount_remote() mount failed, retry with filesystem")
            # try to mount with filesystem
            mount=self.xmlrpc.GetDevicesInfo(device="%s %s" %(device, fstype), mode=mode)
            if mount != mnt_point:
                return False
        return True

    def mounter_local(self, local_mount_point, remote_mnt, device="", label="",mode="mount"):
        if mode == "mount":
            if not os.path.isdir(local_mount_point):
                os.mkdir (local_mount_point)
            self.exe_cmd("ltspfs %s:%s %s" %(shared.remotehost, remote_mnt, local_mount_point) )
            
            # send notification
            self.show_notification( 
            _("Mounting device %(device)s in \n%(mnt_point)s\nPlease wait..." )\
             %{"device":device, "mnt_point":local_mount_point}, urgency=pynotify.URGENCY_NORMAL )
        
        if mode == "umount":
            if os.path.isdir(local_mount_point):
                print_debug ( "mounter_local() umounting %s" %(local_mount_point) )
                self.exe_cmd("fusermount -u %s" %(local_mount_point) )
                print_debug ( "mounter_local() removing dir %s" %(local_mount_point) )
                os.rmdir(local_mount_point)
            
            mydevice=""
            for dev in self.mounted:
                if local_mount_point == self.mounted[dev]:
                    mydevice=device
                
            self.show_notification( _("Umounting device %s.\nPlease wait..." ) %(mydevice)\
             , urgency=pynotify.URGENCY_NORMAL )
            

    def get_local_mountpoint(self, data):
        desktop=os.path.expanduser("~/Desktop")
        
        #fslabel=self.get_value(data, "ID_FS_LABEL")
        #fsvendor=self.get_value(data, "ID_VENDOR")
        fslabel=data['ID_FS_LABEL']
        fsvendor=data['ID_VENDOR']
        counter=1
        if fslabel != "":
            print_debug ( "get_local_mountpoint() have label...." )
            if not os.path.isdir(desktop + "/" + fslabel):
                print_debug ( "get_local_mountpoint() %s dir not exists, returning..." %(desktop + "/" + fslabel) )
                return desktop + "/" + fslabel
            else:
                print_debug ( "get_local_mountpoint() %s dir exists, searching for numbered dirs..." %(desktop + "/" + fslabel) )
                while True:
                    if not os.path.isdir(desktop + "/" + fslabel + "-" + str(counter) ):
                        print_debug ( "get_local_mountpoint() %s dir not exists, returning..." %(desktop + "/" + fslabel + "-" + str(counter)) )
                        return desktop + "/" + fslabel + "-" + str(counter)
                    counter+=1
        if fsvendor != "":
            print_debug ( "get_local_mountpoint() have vendor not label...." )
            if not os.path.isdir(desktop + "/" + fsvendor):
                print_debug ( "get_local_mountpoint() %s dir not exists, returning..." %(desktop + "/" + fsvendor) )
                return desktop + "/" + fsvendor
            else:
                print_debug ( "get_local_mountpoint() %s dir exists, searching for numbered dirs..." %(desktop + "/" + fsvendor) )
                while True:
                    if not os.path.isdir(desktop + "/" + fsvendor + "-" + str(counter) ):
                        print_debug ( "get_local_mountpoint() %s dir not exists, returning..." %(desktop + "/" + fsvendor + "-" + str(counter)) )
                        return desktop + "/" + fsvendor + "-" + str(counter)
                    counter+=1
        else:
            mnt=_("usbdisk")
            print_debug ( "get_local_mountpoint() don't have label or vendor" )
            if not os.path.isdir(desktop + "/" + mnt):
                print_debug ( "get_local_mountpoint() %s dir not exists, returning..." %(desktop + "/" + mnt) )
                return desktop + "/" + mnt
            else:
                print_debug ( "get_local_mountpoint() %s dir exists, searching for numbered dirs..." %(desktop + "/" + mnt) )
                while True:
                    if not os.path.isdir(desktop + "/" + mnt + "-" + str(counter) ):
                        print_debug ( "get_local_mountpoint() %s dir not exists, returning..." %(desktop + "/" + mnt + "-" + str(counter)) )
                        return desktop + "/" + mnt + "-" + str(counter)
                    counter+=1
    
    def floppy(self, action):
        action=action[0]
        print_debug("floppy call %s" %action)
        desktop=os.path.expanduser("~/Desktop")
        local_mount_point=os.path.join(desktop, _("Floppy") )
        
        if action == "mount":
            if not self.mounter_remote("/dev/fd0", "", mode="--mount"):
                self.show_notification (  _("Can't mount floppy")  )
                return
            self.mounter_local(local_mount_point, "/mnt/fd0", device="/dev/fd0", label=_("Floppy"), mode="mount")
            self.launch_desktop_filemanager(local_mount_point)
            self.update_floppy()
            return
        if action == "umount":
            self.mounter_local(local_mount_point, "/mnt/fd0", device="/dev/fd0", label=_("Floppy"), mode="umount")
            
            if not self.mounter_remote("/dev/fd0", "", mode="--umount"):
                self.show_notification (  _("Can't umount floppy")  )
                return
            self.update_floppy()
                
        
    def cdrom(self, *args):
        action=args[0][0]
        cdrom_device=args[0][1]
        desktop=os.path.expanduser("~/Desktop")
        local_mount_point=os.path.join(desktop, _("Cdrom_%s" %cdrom_device) )
        absdev="/dev/%s"%cdrom_device
        
        if action == "mount":
            print_debug ( "cdrom() remote_mnt=%s device=%s" %("/mnt/%s"%cdrom_device, cdrom_device) )
            if not self.mounter_remote(absdev, "", mode="--mount"):
                self.show_notification (  _("Can't mount cdrom")  )
                return
            self.mounter_local(local_mount_point, "/mnt/%s"%cdrom_device, device=absdev, label=_("Cdrom_%s" %cdrom_device), mode="mount")
            
            # change status
            self.update_cdrom(cdrom_device)
            self.launch_desktop_filemanager(local_mount_point)
            return
            
        if action == "umount":
            print_debug ( "cdrom() remote_mnt=%s device=%s" %("/mnt/%s"%cdrom_device, cdrom_device) )
        
            self.mounter_local(local_mount_point, "/mnt/%s"%cdrom_device, device=absdev, label=_("Cdrom_%s" %cdrom_device), mode="umount")
            
            if not self.mounter_remote(absdev, "", mode="--umount"):
                self.show_notification (  _("Can't umount cdrom")  )
                return
            
            # change status
            self.update_cdrom(cdrom_device)
            return

    def usb(self, *args):
        data=args[0]
        if type(data) == type( () ): data=args[0][0]
        
        device=data['DEVNAME']
        action=data['ACTION']
        if not data.has_key('ID_FS_TYPE'):
            # we don't have a filesystem only a full device (ex: /dev/sda)
            vendor=data['ID_VENDOR']
            model=data['ID_MODEL']
            if action == "add":
                self.show_notification( _("From terminal %(host)s.\nConnected USB device %(device)s\n%(vendor)s %(model)s" ) \
                %{"host":shared.remotehost, "device":device, "vendor":vendor, "model":model } )
            if action == "remove":
                self.show_notification( _("From terminal %(host)s.\nDisconnected USB device %(device)s\n%(vendor)s %(model)s" ) \
                %{"host":shared.remotehost, "device":device, "vendor":vendor, "model":model } ) 
            return
        
        else:
            # we have a filesystem ex: /dev/sda1
            fstype=data['ID_FS_TYPE']
            
            usb_status=self.xmlrpc.GetDevicesInfo(device=device, mode="--getstatus").replace('\n','')
            if usb_status == "0":
                mount=True
                n=1
            else:
                mount=False
                n=2
            
            # add to menu
            devid=device.split('/')[2]
            remote_mnt="/mnt/%s" %(devid)
            if action == "add":
                ##########################################
                self.systray.register_device("usb_%s"%devid, 
                                _("USB device %s" %devid), 
                                "usb%s.png"%n, True, 
                                {
                            "usb_%s_mount" %devid: [ _("Mount USB device %s" %(devid)),  "usb_mount.png", mount,  None, device],
                            "usb_%s_umount" %devid: [ _("Umount USB device %s" %(devid)), "usb_umount.png", not mount, None, device]
                                }, 
                                device)
                
                self.systray.register_action("usb_%s_mount" %devid , self.usb, {
                                        "DEVNAME": device, "ACTION": "mount", "ID_FS_TYPE": fstype
                                                                                } 
                                            )
                self.systray.register_action("usb_%s_umount" %devid , self.usb, {
                                        "DEVNAME": device, "ACTION": "umount", "ID_FS_TYPE": fstype
                                                                                }
                                             )
                
                if not self.mounter_remote(device, fstype, "--mount"):
                    self.show_notification (  _("Error, can't mount device %s") %(device)  )
                    return
                
                
                local_mount_point = self.get_local_mountpoint(data)
                label = os.path.basename(local_mount_point)
                
                # mount with fuse and ltspfs    
                self.mounter_local(local_mount_point, remote_mnt, device=device, label=label, mode="mount")
                
                # launch desktop filemanager
                self.launch_desktop_filemanager(local_mount_point)
                self.mounted[device]=local_mount_point
                ##########################################
                
                
            if action == "remove" or action == "umount":
                if action == "remove":
                    print_debug ("usb() UNREGISTER SERVICE")
                    self.systray.unregister_device("usb_%s"%devid)
                if device in self.mounted:
                    local_mount_point=self.mounted[device]
                    label = os.path.basename(local_mount_point)
                else:
                    print_debug ( "remove_usb() device %s not found in self.mounted" %(device) )
                    return
                # umount local fuse
                # check if fuse is mounted
                status=self.exe_cmd("mount |grep -c %s" %(local_mount_point) )
                if int(status) != 0:
                    self.mounter_local(local_mount_point, remote_mnt, device=device, label=label, mode="umount")
                
                # umount remote device
                # check if remote is mounted (user can umount before from desktop icon)
                status=self.xmlrpc.GetDevicesInfo(device=device, mode="--getstatus").replace('\n','')
                try:
                    status=int(status)
                    if status == 0:
                        print_debug ( "remove_usb() device=%s seems not mounted" %(device) )
                    else:
                        if not self.mounter_remote(device, fstype, "--umount"):
                            self.show_notification (  _("Error, can't mount device %s") %(device)  )
                            return
                except ValueError:
                    print_debug ( "error loading device status" )
                
                
                if device in self.mounted:
                    del self.mounted[device]
                else:
                    print_debug ( "remove_usb() devive=%s not in self.mounted dictionary" )
        

    def update_usb(self, *args):
        #print_debug ("update_usb()")
        data=args[0]
        action=data['ACTION']
        device="/dev/%s" %data['DEVPATH'].split('/')[2]
        
        if( len( data['DEVPATH'].split('/') ) ) > 3:
            devid=data['DEVPATH'].split('/')[3]
        else:
            devid=data['DEVPATH'].split('/')[2]
        
        if action ==  "umount":
            self.show_notification (  _("USB device %s umounted. You can extract it." %(device))  )
            
        if action ==  "mount":
            self.show_notification (  _("USB device %s mounted. Ready for use." %(device))  )
        
        usb_status=self.xmlrpc.GetDevicesInfo(device, mode="--getstatus").replace('\n','')
        if usb_status == "0":
            ismounted=False
            n=1
        else:
            ismounted=True
            n=2
        print_debug ("update_usb() usb devid=%s ismounted=%s" %(devid, ismounted) )
        #self.systray.items["usb_"%devid][1]="usb%s.png"%n
        self.systray.update_status("usb_%s"%devid, "usb_%s_mount"%devid, not ismounted)
        self.systray.update_status("usb_%s"%devid, "usb_%s_umount"%devid, ismounted)

        
    def remove_dupes(self, mylist):
        """
        check for duplicate events, 
        kernel create 3-4 umount events before mounting a device
        the events are created and diff at max 1 second
        """
        if len(mylist) != 1:
            have_umount=False
            have_mount=False
            umount_index=None
            nodupes=[]
            nodupes=[ u for u in mylist if u not in locals()['_[1]'] ]
            
            # if have ACTION=umount and ACTION=mount and 
            # DEVPATH is the same remove ACTION=umount
            for event in nodupes:
                action=self.get_value(event.split('#'), "ACTION")
                if action == "umount":
                    have_umount=True
                    umount_index=event
                if action == "mount": have_mount=True
            
            if have_mount and have_umount:
                for i in range(len(nodupes)):
                    if self.get_value(nodupes[i].split('#'), "ACTION") == "umount":
                        #print_debug ( "remove_dupes() Deleting umount ACTION: %s" %nodupes[i] )
                        del nodupes[i]
                        break
            mylist=nodupes
        return mylist



    def get_value(self, data, key=None):
        """
           returns value of given key, example:
              data=["ID_BUS=usb", "DEVICE=/dev/sda", "FSTYPE=vfat"]
              if key="DEVICE"
                returns "/dev/sda" 
            udev current avalaible keys:
             "ID_BUS" "DEVNAME" "ACTION" "ID_FS_LABEL" "ID_FS_TYPE" "ID_VENDOR" "ID_MODEL" "DEVPATH"
        """
        #print_debug ( "::==> get_value() searching for \"%s\"" %key )
        for uvar in data:
            if uvar.split('=')[0] == key:
                print_debug ( "::==> get_value() FOUND key=%s value=%s" %(key, uvar.split('=')[1]) )
                return uvar.split('=')[1]
        # return empty string if not found
        return ""


    def get_desktop(self):    
        is_gnome=self.exe_cmd("ps ux |grep gnome-panel  |grep -c -v grep"  )
        is_kde = self.exe_cmd("ps ux |grep   startkde   |grep -c -v grep"  )
        is_xfce= self.exe_cmd("ps ux |grep xfce4-session|grep -c -v grep"  )
        if int(is_gnome) > 0:
            return "gnome"
        elif int(is_kde) > 0:
            return "kde"
        elif int(is_xfce) > 0:
            return "xfce4"
        else:
            return ""

    def launch_desktop_filemanager(self, path=""):
        if self.desktop == "gnome":
            os.system("nautilus %s" %(path) )
        elif self.desktop == "kde":
            os.system("konqueror %s" %(path) )
        elif self.desktop == "xfce4":
            os.system("Thunar %s" %(path) )
        else:
            print_debug (  "launch_desktop_filemanager() unknow desktop, not launching filemanager" )
            

    
    def exe_cmd(self, cmd, verbose=1):
        import popen2
        output=[]
        (stdout, stdin) = popen2.popen2(cmd)
        stdin.close()
        for line in stdout:
            if line != '\n':
                line=line.replace('\n', '')
                output.append(line)
        if len(output) == 1:
            return output[0]
        elif len(output) > 1:
            if verbose==1:
                print_debug ( "get_result(%s) %s" %(cmd, output) )
            return output
        else:
            if verbose == 1:
                print_debug ( "get_result(%s)=None" %(cmd) )
            return []
  
    def exit(self):
        print_debug ( "FIXME do some thing before quiting..." )
        # say udev_daemon loop to quit
        self.quitting=True
        self.mainloop.quit()
    
    def run (self):
        self.mainloop = gobject.MainLoop()
        try:
            self.mainloop.run()
        except KeyboardInterrupt: # listen Ctrl+C
            self.exit()    



    
if __name__ == "__main__":
    
    # init app
    app=TcosDevicesNG()
    
    # start gui in a thread
    tcosdevices=threading.Thread(target=app.run )
    tcosdevices.start()
    
    # start udev loop
    while True:
        try:
            if app.quitting: break
            app.udev_daemon()
            time.sleep(3)
        except KeyboardInterrupt:
            break
        
    # join gui thread    
    tcosdevices.join()
    sys.exit(0)
    
