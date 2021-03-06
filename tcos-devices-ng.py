#!/usr/bin/env python
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

import os, sys
import gobject
import getopt
from gettext import gettext as _
import time
import socket


CONF_FILE="~/.tcos-devices-ng.conf"
ALL_CONF_FILE="/etc/tcos/tcos-devices-ng.conf"


import pygtk
pygtk.require('2.0')
import gtk

from tcosmonitor import shared
# check for local DISPLAY
remotehost=display=""
if "DISPLAY" in os.environ and os.environ['DISPLAY'] != '':
    remotehost=str(shared.parseIPAddress(os.environ["DISPLAY"]))

action = ""

if remotehost == "":
    print ("tcos-devices-ng: Not allowed to run in local DISPLAY")
    sys.exit(0)

# load conf file and exit if not active
if not shared.test_start("tcos-devices-ng") :
    print ("tcos-devices-ng disabled at %s" % (shared.module_conf_file))
    sys.exit(1)


from tcosmonitor.TcosTrayIcon2 import TcosTrayIcon
import threading

import pynotify
import pwd

# tell gtk we use threads
gtk.gdk.threads_init()




def usage():
    print ("tcos-devices-ng help:")
    print ("")
    print ("   tcos-devices-ng -d [--debug]  (write debug data to stdout)")
    print ("   tcos-devices-ng -h [--help]   (this help)")

try:
    opts, args = getopt.getopt(sys.argv[1:], ":hd", ["help", "debug" ])
except getopt.error, msg:
    print (msg)
    print ("for command line options use tcos-devices-ng --help")
    sys.exit(2)


# process options
for o, a in opts:
    if o in ("-d", "--debug"):
        shared.debug = True
    if o in ("-h", "--help"):
        usage()
        sys.exit()






def log( message ):
    print ( "%d %s" % (os.getpid(), message) )
    
def print_debug(txt):
    if shared.debug:
        print >>sys.stderr, "%d %s::%s" % (os.getpid(), "tcos-devices-ng", txt)
        #print("%d %s::%s" % (os.getpid(), "tcos-devices-ng", txt), file=sys.stderr)




class TcosDevicesNG:
    def __init__(self):
        self.host=None
        self.hostname=None
        self.name="TcosDevicesNG"
        self.mounted={}
        self.mntconf={}
        self.username=None
        self.loadconf(CONF_FILE)
        self.loadconf(ALL_CONF_FILE)
        
        ######## Create icon #############
        disable_quit=self.mntconf.has_key("disable_quit") and self.mntconf['disable_quit'] == "1"
        enable_reboot_and_poweroff=self.mntconf.has_key("enable_reboot_poweroff") and self.mntconf['enable_reboot_poweroff'] == "1"
        self.systray=TcosTrayIcon(disable_quit=disable_quit, allow_reboot_poweroff=enable_reboot_and_poweroff)
        
        
        self.systray.status=True
        
        self.initremote()
        self.desktop=self.get_desktop()
        
        ######## read floppys #############
        if self.mntconf.has_key("disable_floppy") and self.mntconf['disable_floppy'] == "1" :
            print_debug("__init__() floppy disabled from CONF_FILE")    
        else:
            self.getremote_floppy()
        
        ######## read cdroms #############
        if self.mntconf.has_key("disable_cdroms") and self.mntconf['disable_cdroms'] == "1" :
            print_debug("__init__() cdroms disabled from CONF_FILE")    
        else:
            self.getremote_cdroms()
        
        ######## read hard disk #############
        if self.mntconf.has_key("disable_hdd") and self.mntconf['disable_hdd'] == "1" :
            print_debug("__init__() hdd disabled from CONF_FILE")    
        else:
            self.getremote_hdd()
        
        self.quitting=False
        
        # register quit event
        if not disable_quit:
            self.systray.register_action("quit", lambda w: self.exit() )
        
        # register reboot and poweroff
        if enable_reboot_and_poweroff:
            self.systray.register_action("reboot", self.menu_remote_reboot_poweroff, 'reboot'  )
            self.systray.register_action("poweroff", self.menu_remote_reboot_poweroff, 'poweroff' )
        
        self.udev_events={ 
        "insert":         {"ID_BUS":  "usb",         "ACTION":"add"}, 
        "remove":         {"ID_BUS":  "usb",         "ACTION":"remove"},
        "insert-firewire":{"ID_BUS":  "ieee1394",    "ACTION":"add"}, 
        "remove-firewire":{"ID_BUS":  "ieee1394",    "ACTION":"remove"},
        "mount-floppy":   {"DEVPATH": "/block/fd0",  "ACTION":"mount"},
        "umount-floppy":  {"DEVPATH": "/block/fd0",  "ACTION":"umount"},
        "mount-cdrom":    {"DEVPATH": "/block/hd*",   "ACTION":"mount"},
        "umount-cdrom":   {"DEVPATH": "/block/hd*",   "ACTION":"umount"}, 
        "mount-flash":    {"DEVPATH": "/block/sd*",   "ACTION":"mount"},
        "umount-flash":   {"DEVPATH": "/block/sd*",   "ACTION":"umount"},
        "newcdrom":       {"ID_FS_TYPE":"iso9660",    "ACTION":"add"}
        }

    def menu_remote_reboot_poweroff(self, *args):
        try:
            action=args[0][0]
        except Exception, err:
            print_debug("menu_remote_reboot_poweroff() Exception, error=%s"%err)
            return
        remote_hostname=self.xauth.get_hostname()
        xauth_cookie=self.xauth.get_cookie()
        if self.mntconf.has_key("reboot_poweroff_timeout"):
            timeout=self.mntconf['reboot_poweroff_timeout']
        else:
            timeout="5"

        if action == "reboot":
            self.show_notification( _("Rebooting in %s seconds") %(timeout) )
        elif action == "poweroff":
            self.show_notification( _("Shutting down in %s seconds") %(timeout) )
        else:
            # unknow signal
            return
        print_debug("remote_reboot_poweroff() action=%s, remote_hostname=%s, xauth_cookie=%s"%(action, remote_hostname, xauth_cookie))
        cmd=threading.Thread(target=self.remote_reboot_poweroff, args=[action, timeout,  xauth_cookie, remote_hostname] )
        cmd.start()
        return

    def remote_reboot_poweroff(self, action, timeout, xauth_cookie, remote_hostname):
        print_debug("remote_reboot_poweroff() waiting %s seconds"%timeout)
        #time.sleep(int(timeout))
        try:
            result=self.xmlrpc.tc.tcos.rebootpoweroff( action, timeout, xauth_cookie, remote_hostname)
            print_debug("remote_reboot_poweroff() result=%s"%result.strip())
            if result.startswith("error"):
                self.show_notification( _("ERROR during action %(action)s:\n%(errortxt)s") %{"action":action, "errortxt":result.replace('error: ','')} )
        except Exception, err:
            print_debug("remote_reboot_poweroff() Exception: %s"%err)
            self.show_notification( _("ERROR during action %(action)s:\n%(errortxt)s") %{"action":action, "errortxt":err} )
            return

    def loadconf(self, conffile):
        print_debug ( "loadconf() __init__ conffile=%s" %conffile )
        conf=os.path.expanduser(conffile)
        if os.path.isfile(conf):
            print_debug ("loadconf() found conf file %s" %conf)
            f=open(conf, "r")
            data=f.readlines()
            f.close()
            for line in data:
                if line == '\n': continue
                if line.find('#') == 0: continue
                line=line.replace('\n', '')
                if "=" in line:
                    try:
                        self.mntconf["%s"%line.split('=')[0]] = line.split('=')[1]
                    except Exception, err:
                        print_debug("loadconf() Exception, error=%s"%err)
                        pass
        print_debug( "loadconf mntconf=%s" %self.mntconf )
        return
   
    def show_notification(self, msg, urgency=pynotify.URGENCY_CRITICAL, timeout=20000):
        pynotify.init("tcos-devices-ng")
        if os.path.isfile("/usr/share/pixmaps/tcos-icon-32x32-custom.png"):
            image_uri="file://usr/share/pixmaps/tcos-icon-32x32-custom.png"
        else:
            image_uri="file://" + os.path.abspath(shared.IMG_DIR) + "/tcos-devices-32x32.png"
        n = pynotify.Notification( _("Tcos device daemon") , msg, image_uri )
        n.set_urgency(urgency)
        # don't attach to status icon with multiple notifications
        #if hasattr(pynotify.Notification, 'attach_to_status_icon'):
        #    n.attach_to_status_icon(self.systray.statusIcon)
        n.set_category("device")
        n.set_timeout(timeout) # 15 sec
        if not n.show():
            print_debug  ("show_notification() Failed to send notification")
        
  
    def initremote(self):
        # get all devices
        import tcosmonitor.TcosXmlRpc
        import tcosmonitor.TcosConf
        import tcosmonitor.TcosCommon
        import tcosmonitor.TcosXauth
        
        self.xauth=tcosmonitor.TcosXauth.TcosXauth(self)
        self.xauth.init_standalone()
        
        self.common=tcosmonitor.TcosCommon.TcosCommon(self)
        print_debug ( "loading config class..." )
        
        self.config=tcosmonitor.TcosConf.TcosConf(self, openfile=False)
        self.xmlrpc=tcosmonitor.TcosXmlRpc.TcosXmlRpc(self)
        
        self.username=self.common.get_username()
        self.host=self.common.get_display(ip_mode=True)
        self.hostname=self.common.get_display(ip_mode=False)
        
        print_debug("initremote() username=%s host=%s hostname=%s"%(self.username, self.host, self.hostname))
        
        if not self.common.user_in_group("fuse"):
            print ("tcos-devices-ng: ERROR: User not in group fuse")
            shared.error_msg(_("TCOS_DEVICES: Your user is not in group fuse and you can not use USB devices. Please contact with your administrator."))
            sys.exit(1)
        nossl=True
        # make a test and exit if no cookie match
        if not self.xauth.test_auth(nossl):
            print ("tcos-devices-ng: ERROR: Xauth cookie don't match")
            sys.exit(1)
            
        self.xmlrpc.newhost(self.host, nossl)
        if not self.xmlrpc.connected:
            print ( _("Error connecting with TcosXmlRpc in %s.") %(self.host) )
            sys.exit(1)
        
        # check for enabled devices
        disable_usb=self.xmlrpc.IsEnabled("TCOS_DISABLE_USB")
        disable_ide=self.xmlrpc.IsEnabled("TCOS_DISABLE_IDE")
        if disable_usb or disable_ide:
            print ("tcos-devices-ng: TCOS_DISABLE_USB or TCOS_DISABLE_IDE enabled, exiting...")
            sys.exit(0)

    def get_desktop_path(self):
        try:
            desktop=self.common.exe_cmd("/usr/lib/tcos/get-xdg-desktop", verbose=1, background=False, lines=0, cthreads=0)
        except:
            desktop=os.path.expanduser("~/")
        if not os.path.isdir(desktop):
            desktop=os.path.expanduser("~/")
        return desktop

    def getremote_cdroms(self):
        self.cdrom_devices=self.xmlrpc.GetDevicesInfo(device="", mode="--getcdrom").split('|')
        self.cdrom_devices=self.cdrom_devices[0:-1]
        print_debug ( "get_data() cdroms=%s" %(self.cdrom_devices) )
        for cdrom in self.cdrom_devices:
            # get device status
            cdrom_status= self.xmlrpc.GetDevicesInfo(device="/dev/%s" %cdrom, mode="--getstatus")
            if cdrom_status == "0":
                mount=True
                umount=False
            else:
                mount=False
                umount=True
            cdrom_desc = self.xmlrpc.GetDevicesInfo(device="/dev/%s" %cdrom, mode="--getid")
            self.systray.register_device("cdrom_%s"%cdrom, 
                            _("Cdrom device %s" ) %cdrom, 
                            "cdrom.png", True, 
                            {
                        "cdrom_%s_mount" %cdrom: [ _("Mount Cdrom"),  "cdrom_mount.png", mount,  None, "/dev/%s"%cdrom],
                        "cdrom_%s_umount"%cdrom: [ _("Umount Cdrom"), "cdrom_umount.png", umount, None, "/dev/%s"%cdrom]
                            }, 
                            "/dev/%s"%(cdrom),
                            cdrom_desc)
            self.systray.register_action("cdrom_%s_mount" %cdrom, self.cdrom, "mount", cdrom )
            self.systray.register_action("cdrom_%s_umount" %cdrom, self.cdrom, "umount", cdrom )

    def getremote_hdd(self):
        self.hdd_devices=self.xmlrpc.GetDevicesInfo(device="", mode="--gethdd").split('|')
        self.hdd_devices=self.hdd_devices[0:-1]
        print_debug ( "getremote_hdd() hdd=%s" %(self.hdd_devices) )
        for hdd in self.hdd_devices:
            # get device status
            hdd_status= self.xmlrpc.GetDevicesInfo(device="/dev/%s" %hdd, mode="--getstatus")
            if hdd_status == "0":
                mount=True
                umount=False
            else:
                mount=False
                umount=True
            hdd_desc = self.xmlrpc.GetDevicesInfo(device="/dev/%s" %hdd[0:3], mode="--getid")
            self.systray.register_device("hdd_%s"%hdd, 
                            _("Disk partition %s") %hdd, 
                            "hdd_mount.png", True, 
                            {
                        "hdd_%s_mount" %hdd: [ _("Mount disk partition"),  "hdd_mount.png", mount,  None, "/dev/%s"%hdd],
                        "hdd_%s_umount"%hdd: [ _("Umount disk partition"), "hdd_umount.png", umount, None, "/dev/%s"%hdd]
                            }, 
                            "/dev/%s"%(hdd),
                            hdd_desc)
            self.systray.register_action("hdd_%s_mount" %hdd, self.hdd, "mount", hdd )
            self.systray.register_action("hdd_%s_umount" %hdd, self.hdd, "umount", hdd )



    def getremote_floppy(self):
        have_floppy=self.xmlrpc.GetDevicesInfo(device="/dev/fd0", mode="--exists")
        if have_floppy == "0":
            print_debug ( _("No floppy detected") )
            return
        floppy_status=self.xmlrpc.GetDevicesInfo(device="/dev/fd0", mode="--getstatus")
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
        floppy_status=self.xmlrpc.GetDevicesInfo(device="/dev/fd0", mode="--getstatus")
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

    def update_hdd(self, *args):
        if len(args) > 0:
            if args[0] == "mount":
                self.show_notification (  _("Hard disk partition mounted. Ready for use.")  )
                return
            elif args[0] == "umount":
                self.show_notification (  _("Hard disk partition umounted.")  )
                return
            else:
                dev=args[0]
        hdd_status=self.xmlrpc.GetDevicesInfo(device="/dev/%s"%dev, mode="--getstatus")
        if hdd_status == "0":
            ismounted=False
            n=1
        else:
            ismounted=True
            n=2
        print_debug ("update_hdd() hdd ismounted=%s" %ismounted)
        self.systray.update_status("hdd_%s"%dev, "hdd_%s_mount"%dev, not ismounted)
        self.systray.update_status("hdd_%s"%dev, "hdd_%s_umount"%dev, ismounted)



    def update_cdrom(self, dev, action=None):
        if action == "mount" or action == "umount":
            devtype=self.xmlrpc.GetDevicesInfo(device=dev, mode="--cdaudio")
            if action == "mount":
                if devtype == "1":
                    self.show_notification ( _("Audio cdrom mounted., you can listen music opening wav files.") )
                else:
                    self.show_notification (  _("Cdrom mounted. Ready for use.")  )
                return
            elif action == "umount":
                self.show_notification (  _("Cdrom umounted. You can extract it.")  )
                return
            
        cdrom_status=self.xmlrpc.GetDevicesInfo(device="/dev/%s"%dev, mode="--getstatus")
        if cdrom_status == "0":
            ismounted=False
            n=1
        else:
            ismounted=True
            n=2
        print_debug ("update_cdrom() cdrom ismounted=%s" %ismounted)
        self.systray.update_status("cdrom_%s"%dev, "cdrom_%s_mount"%dev, not ismounted)
        self.systray.update_status("cdrom_%s"%dev, "cdrom_%s_umount"%dev, ismounted)


    def udev_daemon(self):
        start1=time.time()
        print_debug ("udev_daemon() starting...")
        udev=self.xmlrpc.GetDevicesInfo(device="", mode="--getudev").split('|')
        print_debug("udev_daemon GetDevicesInfo time=%f" %(time.time() - start1) )
        if "error" in " ".join(udev): return
        udev=udev[:-1]
        if len(udev) < 1 or udev[0] == "unknow": return
        udev=self.remove_dupes(udev)
        for line in udev:
            data={}
            tmp=line.split('#')
            for i in tmp:
                if '=' in i:
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
        #print_debug ("do_udev_event() data=%s" %data)
        if data.has_key("ID_FS_TYPE") and data['ID_FS_TYPE'] == "iso9660":
            # newcdrom ADD (mount it)
            if data['ACTION'] == "add":
                self.cdrom( ('mount', data["DEVPATH"].split("/")[2]), )
            else:
                if data['ACTION'] == "mount":
                    # check if CDROM is automonted before
                    if self.xmlrpc.GetDevicesInfo(device=data["DEVPATH"], mode="--getstatus") == "1":
                        return
                self.cdrom( (data['ACTION'], data["DEVPATH"].split("/")[2]), )
        
        if data.has_key("ID_BUS") and data["ID_BUS"] == "usb":
            if data.has_key("DEVPATH") and "/block/sr" in data["DEVPATH"]:
                self.cdrom_usb(data)
            else:
                self.usb(data)
        
        if data.has_key("ID_BUS") and data["ID_BUS"] == "ieee1394":
            self.firewire(data)
        
        if data.has_key("DEVPATH") and "/block/hd" in data["DEVPATH"]:
            if len(data["DEVPATH"].split('/')) > 3:
                # we have a hdd
                self.update_hdd(data["ACTION"])
            else:
                # we have a cdrom
                self.update_cdrom("/dev/" + data["DEVPATH"].split("/")[2], action=data["ACTION"])
            
        if data.has_key("DEVPATH") and "/block/fd" in data["DEVPATH"]:
            self.update_floppy(data["ACTION"])
        
        if data.has_key("DEVPATH") and data["ID_BUS"] == "ieee1394" and "/block/sd" in data["DEVPATH"]:
            # FIXME SATA devices not detected as HDD
            self.update_firewire(data)
        elif data.has_key("DEVPATH") and "/block/sd" in data["DEVPATH"]:
            self.update_usb(data)
        
    def mounter_remote(self, device, fstype, mode="--mount"):
        print_debug ( "mounter_remote() device=%s fstype=%s" %(device, fstype) )
        if device == None:
            return False
        mnt_point="/mnt/%s" %(device[5:])
        if mode == "--mount":
            # send notification
            self.show_notification( _("Mounting device %s\nPlease wait..." ) %(device), urgency=pynotify.URGENCY_NORMAL )
             
            print_debug ( "mount_remote() mounting device=%s fstype=%s mnt_point=%s" %(device, fstype, mnt_point) )
        elif mode == "--umount":
            print_debug ( "mount_remote() umounting device=%s fstype=%s mnt_point=%s" %(device, fstype, mnt_point) )
        
        # set socket timeout bigger (floppy can take some time)
        socket.setdefaulttimeout(15)
        
        if fstype != "vfat":
            # if we know that device is vfat dont try to get type again
            dtype=self.xmlrpc.GetDevicesInfo(device=device, mode="--gettype")
            if dtype == "ntfs-3g" and mode == "--mount":
                print_debug ( "mounter_remote() Ummm mounting a NTFS-3G, creating a thread" )
                # create a thread
                try:
                    ntfs_3g=threading.Thread(target=self.xmlrpc.GetDevicesInfo, args=(device,mode) )
                    ntfs_3g.start()
                    return True
                except Exception, err:
                    print_debug("ntfs-3g thread Exception, error=%s"%err)
                    return True
        
        # set socket timeout bigger (floppy can take some time)
        socket.setdefaulttimeout(15)

        mount=self.xmlrpc.GetDevicesInfo(device=device, mode=mode)
        if mount != mnt_point:
            print_debug ( "mounter_remote() mount failed, retry with filesystem")
            print_debug ( "mounter_remote() FIRST ERROR mount='%s' mnt_point='%s'" %(mount, mnt_point))
            return False
            """
            # try to mount with filesystem
            mount=self.xmlrpc.GetDevicesInfo(device="%s %s" %(device, fstype), mode=mode)
            if mount != mnt_point:
                print_debug ("mounter_remote() SECOND ERROR mount='%s' mnt_point='%s'" %(mount, mnt_point))
                return False
            """
        print_debug("mounter_remote(device=%s fstype=%s) mount OK"%(device, fstype))
        return True

    def mounter_local(self, local_mount_point, remote_mnt, device="", label="", mode="mount"):
        if mode == "mount":
            if not os.path.isdir(local_mount_point):
                os.mkdir (local_mount_point)
                # wait until appear in desktop icon folder
                time.sleep(2)
            output=self.common.exe_cmd("ltspfs %s:%s %s 2>&1" %(self.host, remote_mnt, local_mount_point), verbose=1, background=False, lines=0, cthreads=0)
            if "ERROR" in output:
                self.show_notification( _("Error mounting LTSPFS, check versions of LTSPFS packages"), urgency=pynotify.URGENCY_CRITICAL)
                return False
            
            """
            # DISABLED: too late to show notification better in mounter_remote
            # send notification
            self.show_notification( 
            _("Mounting device %(device)s in \n%(mnt_point)s\nPlease wait..." )\
             %{"device":device, "mnt_point":local_mount_point}, urgency=pynotify.URGENCY_NORMAL )
            """
        if mode == "umount":
            if os.path.isdir(local_mount_point):
                print_debug ( "mounter_local() umounting %s" %(local_mount_point) )
                self.common.exe_cmd("fusermount -u %s" %(local_mount_point), verbose=1, background=False, lines=0, cthreads=0 )
                self.common.exe_cmd("fusermount -uz %s 2>/dev/null" %(local_mount_point), verbose=1, background=False, lines=0, cthreads=0 )
                print_debug ( "mounter_local() removing dir %s" %(local_mount_point) )
                try:
                    os.rmdir(local_mount_point)
                except Exception, err:
                    print_debug("mounter_local(umount %s) Exception, error %s"%(local_mount_point, err))
            
            mydevice=""
            for dev in self.mounted:
                if local_mount_point == self.mounted[dev]:
                    mydevice=device
                
            self.show_notification( _("Umounting device %s.\nPlease wait..." ) %(mydevice)\
             , urgency=pynotify.URGENCY_NORMAL )
        return True
            

    def get_local_mountpoint(self, data):
        desktop=self.get_desktop_path()
        
        #fslabel=self.get_value(data, "ID_FS_LABEL")
        #fsvendor=self.get_value(data, "ID_VENDOR")
        if data.has_key("ID_FS_LABEL"):
            fslabel=data['ID_FS_LABEL']
        else:
            fslabel=""
            
        if data.has_key("ID_VENDOR"):
            fsvendor=data['ID_VENDOR']
        else:
            fsvendor=""
            
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
            if data.has_key("ID_BUS") and data["ID_BUS"] == "usb":
                mnt=_("usbdisk")
            else:
                mnt=_("firewiredisk")
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
        desktop=self.get_desktop_path()
        
        if self.mntconf.has_key("fd0"):
            local_mount_point=os.path.join(desktop, self.mntconf['fd0'] )
        else:
            local_mount_point=os.path.join(desktop, _("Floppy") )
        
        if action == "mount":
            if not self.mounter_remote("/dev/fd0", "", mode="--mount"):
                self.show_notification (  _("Can't mount floppy")  )
                return
            if not self.mounter_local(local_mount_point, "/mnt/fd0", device="/dev/fd0", label=_("Floppy"), mode="mount"):
                return
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
        desktop=self.get_desktop_path()
        
        if self.mntconf.has_key(cdrom_device):
            local_mount_point=os.path.join(desktop, self.mntconf[cdrom_device] )
        else:
            local_mount_point=os.path.join(desktop, _("Cdrom_%s") %cdrom_device )
            
        
        absdev="/dev/%s"%cdrom_device
        
        if action == "mount":
            print_debug ( "cdrom() remote_mnt=%s device=%s" %("/mnt/%s"%cdrom_device, cdrom_device) )
            if not self.mounter_remote(absdev, "", mode="--mount"):
                self.show_notification (  _("Can't mount cdrom")  )
                return
            if not self.mounter_local(local_mount_point, "/mnt/%s"%cdrom_device, device=absdev, label=_("Cdrom_%s")  %cdrom_device, mode="mount"):
                return
            
            # change status
            self.update_cdrom(cdrom_device)
            self.launch_desktop_filemanager(local_mount_point)
            return
            
        if action == "umount":
            print_debug ( "cdrom() remote_mnt=%s device=%s" %("/mnt/%s"%cdrom_device, cdrom_device) )
        
            self.mounter_local(local_mount_point, "/mnt/%s"%cdrom_device, device=absdev, label=_("Cdrom_%s") %cdrom_device, mode="umount")
            
            if not self.mounter_remote(absdev, "", mode="--umount"):
                self.show_notification (  _("Can't umount cdrom")  )
                return
            
            # change status
            self.update_cdrom(cdrom_device)
            # eject CDROM
            self.xmlrpc.GetDevicesInfo(device=cdrom_device, mode="--eject")
            return


    def hdd(self, *args):
        action=args[0][0]
        hdd_device=args[0][1]
        desktop=self.get_desktop_path()
        
        if self.mntconf.has_key(hdd_device):
            local_mount_point=os.path.join(desktop, self.mntconf[hdd_device] )
        else:
            local_mount_point=os.path.join(desktop, _("Disk_%s")  %hdd_device )
         
        
        absdev="/dev/%s"%hdd_device
        
        if action == "mount":
            print_debug ( "hdd() remote_mnt=%s device=%s" %("/mnt/%s"%hdd_device, hdd_device) )
            if not self.mounter_remote(absdev, "", mode="--mount"):
                self.show_notification (  _("Can't mount hard disk partition")  )
                return
            if not self.mounter_local(local_mount_point, "/mnt/%s"%hdd_device, device=absdev, label=_("Disk_%s")  %hdd_device, mode="mount"):
                return
            
            # change status
            self.update_hdd(hdd_device)
            self.launch_desktop_filemanager(local_mount_point)
            return
            
        if action == "umount":
            print_debug ( "hdd() remote_mnt=%s device=%s" %("/mnt/%s"%hdd_device, hdd_device) )
        
            self.mounter_local(local_mount_point, "/mnt/%s"%hdd_device, device=absdev, label=_("Disk_%s") %hdd_device, mode="umount")
            
            if not self.mounter_remote(absdev, "", mode="--umount"):
                self.show_notification (  _("Can't umount hard disk partition")  )
                return
            
            # change status
            self.update_hdd(hdd_device)
            return

    def cdrom_usb(self, *args):
        data=args[0]
        if isinstance(data, tuple): data=args[0][0]
        
        print_debug("cdrom_usb() data=%s" %data)
        if data.has_key('DEVPATH'):
            device="/dev/"+data["DEVPATH"].split('/')[2]
        else:
            device=data['DEVNAME']
        action=data['ACTION']
        devid=device.split('/')[2]
        remote_mnt="/mnt/%s" %(devid)

        usb_status=self.xmlrpc.GetDevicesInfo(device=device, mode="--getstatus")
        if usb_status == "0":
            mount=True
            n=1
        else:
            mount=False
            n=2
   
        if action == "add":
            if not data.has_key('ID_VENDOR'):
                vendor=""
            else:
                vendor=data['ID_VENDOR']
            if not data.has_key('ID_MODEL'):
                model=""
            else:
                model=data['ID_MODEL']
            if not data.has_key('ID_FS_TYPE'):
                fstype=""
            else:
                fstype=data['ID_FS_TYPE']
            self.show_notification( _("From terminal %(host)s.\nConnected CDROM USB device %(device)s\n%(vendor)s %(model)s" ) \
            %{"host":self.hostname, "device":device, "vendor":vendor, "model":model } )
            ###########     add USB CDROM device    ############
            self.systray.register_device("usb_%s"%devid, 
                            _("CDROM USB device %s") %devid, 
                            "usb%s.png"%n, True, 
                            {
                        "usb_%s_mount" %devid: [ _("Mount CDROM USB device %s") %(devid),  "usb_mount.png", mount,  None, device],
                        "usb_%s_umount" %devid: [ _("Umount CDROM USB device %s") %(devid), "usb_umount.png", not mount, None, device]
                            }, 
                            device,
                            "%s %s"%(vendor, model))
                
            self.systray.register_action("usb_%s_mount" %devid , self.cdrom_usb, {
                                    "DEVNAME": device, "ACTION": "mount", "ID_FS_TYPE": fstype, "FORCE_MOUNT":True
                                                                            } 
                                        )
            self.systray.register_action("usb_%s_umount" %devid , self.cdrom_usb, {
                                    "DEVNAME": device, "ACTION": "umount", "ID_FS_TYPE": fstype, "FORCE_MOUNT":True
                                                                            }
                                            )
            ###############################################
            # We can have only a cdrom connected without cd inserted
            if fstype != "":
                desktop=self.get_desktop_path()
        
                if self.mntconf.has_key(devid):
                    local_mount_point=os.path.join(desktop, self.mntconf[devid] )
                else:
                    local_mount_point=os.path.join(desktop, _("Cdrom_%s") %devid )
                    
                print_debug ( "cdrom_usb() remote_mnt=%s device=%s" %(remote_mnt, devid) )
                if not self.mounter_remote(device, fstype, mode="--mount"):
                    self.show_notification (  _("Error, can't mount device %s") %(device)  )
                    return

                if device in self.mounted:
                    data['ID_FS_LABEL']=os.path.basename(self.mounted[device])
                    data['ID_VENDOR']=os.path.basename(self.mounted[device])

                # remote device is mounted, mount_local and launch filemanager
                if not self.mounter_local(local_mount_point, remote_mnt, device=device, label=_("Cdrom_%s")  %devid, mode="mount"):
                    return
                self.launch_desktop_filemanager(local_mount_point)
                self.mounted[device]=local_mount_point
        
            # change status
            self.update_cdrom_usb(devid, action)
            return    
                    
        elif action == "mount":
            if not data.has_key('ID_FS_TYPE'):
                fstype=""
            else:
                fstype=data['ID_FS_TYPE']
            desktop=self.get_desktop_path()
    
            if self.mntconf.has_key(devid):
                local_mount_point=os.path.join(desktop, self.mntconf[devid] )
            else:
                local_mount_point=os.path.join(desktop, _("Cdrom_%s") %devid )
                
            print_debug ( "cdrom_usb() remote_mnt=%s device=%s" %(remote_mnt, devid) )
            if not self.mounter_remote(device, fstype, mode="--mount"):
                self.show_notification (  _("Error, can't mount device %s") %(device)  )
                return

            if device in self.mounted:
                data['ID_FS_LABEL']=os.path.basename(self.mounted[device])
                data['ID_VENDOR']=os.path.basename(self.mounted[device])

            # remote device is mounted, mount_local and launch filemanager
            if not self.mounter_local(local_mount_point, remote_mnt, device=device, label=_("Cdrom_%s")  %devid, mode="mount"):
                return
        
            # change status
            self.update_cdrom_usb(devid, action)
            self.launch_desktop_filemanager(local_mount_point)
            self.mounted[device]=local_mount_point
            return
            
        elif action == "remove" or action == "umount":
            if action == "remove":
                if not data.has_key('ID_VENDOR'):
                    vendor=""
                else:
                    vendor=data['ID_VENDOR']
                if not data.has_key('ID_MODEL'):
                    model=""
                else:
                    model=data['ID_MODEL']
                self.show_notification( _("From terminal %(host)s.\nDisconnected CDROM USB device %(device)s\n%(vendor)s %(model)s" ) \
                %{"host":self.hostname, "device":device, "vendor":vendor, "model":model } ) 
                print_debug ("cdrom_usb() UNREGISTER SERVICE")
                self.systray.unregister_device("usb_%s"%devid)
            if device in self.mounted:
                local_mount_point=self.mounted[device]
            else:
                print_debug ( "remove_cdrom_usb() device %s not found in self.mounted" %(device) )
                return
            # umount local fuse
            # check if fuse is mounted
            status=self.common.exe_cmd("mount |grep -c %s" %(local_mount_point), verbose=1, background=False, lines=0, cthreads=0 )
            if int(status) != 0:
                self.mounter_local(local_mount_point, remote_mnt, device=device, label=_("Cdrom_%s") %devid, mode="umount")
            
            # umount remote device
            # check if remote is mounted (user can umount before from desktop icon)
            print_debug("cdrom_usb() GETSTATUS device=%s"%device)
            status=self.xmlrpc.GetDevicesInfo(device=device, mode="--getstatus")
            try:
                status=int(status)
                if status == 0:
                    print_debug ( "remove_cdrom_usb() device=%s seems not mounted" %(device) )
                    self.systray.update_status("usb_%s"%devid, "usb_%s_mount"%devid, True)
                    self.systray.update_status("usb_%s"%devid, "usb_%s_umount"%devid, False)
                    
                else:
                    if not self.mounter_remote(device, "", mode="--umount"):
                        self.show_notification (  _("Can't umount cdrom usb %s") %(device)  )
                        return
                    self.update_cdrom_usb(devid, action)
            except Exception, err:
                print_debug ( "cdrom_usb() Exception error %s"%err )

    def usb(self, *args):
        data=args[0]
        if isinstance(data, tuple): data=args[0][0]
        
        print_debug("usb() data=%s" %data)
        
        device=data['DEVNAME']
        action=data['ACTION']
        if not data.has_key('ID_FS_TYPE'):
            # we don't have a filesystem only a full device (ex: /dev/sda)
            if not data.has_key('ID_VENDOR'):
                vendor=""
            else:
                vendor=data['ID_VENDOR']
            if not data.has_key('ID_MODEL'):
                model=""
            else:
                model=data['ID_MODEL']
            if action == "add":
                self.show_notification( _("From terminal %(host)s.\nConnected USB device %(device)s\n%(vendor)s %(model)s" ) \
                %{"host":self.hostname, "device":device, "vendor":vendor, "model":model } )
            if action == "remove":
                self.show_notification( _("From terminal %(host)s.\nDisconnected USB device %(device)s\n%(vendor)s %(model)s" ) \
                %{"host":self.hostname, "device":device, "vendor":vendor, "model":model } ) 
            return
        
        else:
            # we have a filesystem ex: /dev/sda1
            if not data.has_key('ID_FS_TYPE'):
                fstype=""
            else:
                fstype=data['ID_FS_TYPE']
            
            if fstype == "swap" or fstype == "extended": return
            
            usb_status=self.xmlrpc.GetDevicesInfo(device=device, mode="--getstatus")
            if usb_status == "0":
                mount=True
                n=1
            else:
                mount=False
                n=2
            
            # add to menu
            devid=device.split('/')[2]
            remote_mnt="/mnt/%s" %(devid)
            if action == "add" or action == "mount":
                if action == "add":
                    ###########     add USB  device    ############
                    self.systray.register_device("usb_%s"%devid, 
                                    _("USB device %s") %devid, 
                                    "usb%s.png"%n, True, 
                                    {
                                "usb_%s_mount" %devid: [ _("Mount USB device %s") %(devid),  "usb_mount.png", mount,  None, device],
                                "usb_%s_umount" %devid: [ _("Umount USB device %s") %(devid), "usb_umount.png", not mount, None, device]
                                    }, 
                                    device)
                    
                    self.systray.register_action("usb_%s_mount" %devid , self.usb, {
                                            "DEVNAME": device, "ACTION": "mount", "ID_FS_TYPE": fstype, "FORCE_MOUNT":True
                                                                                    } 
                                                )
                    self.systray.register_action("usb_%s_umount" %devid , self.usb, {
                                            "DEVNAME": device, "ACTION": "umount", "ID_FS_TYPE": fstype, "FORCE_MOUNT":True
                                                                                    }
                                                 )
                    ###############################################
                    
                    if not self.mounter_remote(device, fstype, "--mount"):
                        self.show_notification (  _("Error, can't mount device %s") %(device)  )
                        return
                
                    if device in self.mounted:
                        data['ID_FS_LABEL']=os.path.basename(self.mounted[device])
                        data['ID_VENDOR']=os.path.basename(self.mounted[device])
                
                if action == "mount":
                    # mount from menu and wait for udev mount event
                    if data.has_key("FORCE_MOUNT") and data["FORCE_MOUNT"]:
                        if not self.mounter_remote(device, fstype, "--mount"):
                            self.show_notification (  _("Error, can't mount device %s") %(device)  )
                        return
                
                    # remote device is mounted, mount_local and launch filemanager
                    local_mount_point = self.get_local_mountpoint(data)
                    label = os.path.basename(local_mount_point)
                
                    # mount with fuse and ltspfs    
                    if not self.mounter_local(local_mount_point, remote_mnt, device=device, label=label, mode="mount"):
                        return
                
                    # launch desktop filemanager
                    self.launch_desktop_filemanager(local_mount_point)
                    self.mounted[device]=local_mount_point
                    ##########################################
                
                
            elif action == "remove" or action == "umount":
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
                status=self.common.exe_cmd("mount |grep -c %s" %(local_mount_point), verbose=1, background=False, lines=0, cthreads=0 )
                if int(status) != 0:
                    self.mounter_local(local_mount_point, remote_mnt, device=device, label=label, mode="umount")
                
                # umount remote device
                # check if remote is mounted (user can umount before from desktop icon)
                print_debug("usb() GETSTATUS device =%s"%device)
                status=self.xmlrpc.GetDevicesInfo(device=device, mode="--getstatus")
                try:
                    status=int(status)
                    if status == 0:
                        print_debug ( "remove_usb() device=%s seems not mounted" %(device) )
                        self.systray.update_status("usb_%s"%devid, "usb_%s_mount"%devid, True)
                        self.systray.update_status("usb_%s"%devid, "usb_%s_umount"%devid, False)
                        
                    else:
                        if not self.mounter_remote(device, fstype, "--umount"):
                            self.show_notification (  _("Error, can't mount device %s") %(device)  )
                            return
                except Exception, err:
                    print_debug ( "usb() Exception error %s"%err )
                
                
                #if device in self.mounted:
                #    del self.mounted[device]
                #else:
                #    print_debug ( "remove_usb() devive=%s not in self.mounted dictionary" )
                
    def firewire(self, *args):
        data=args[0]
        if isinstance(data, tuple): data=args[0][0]
        
        print_debug("firewire() data=%s" %data)
        
        device=data['DEVNAME']
        action=data['ACTION']
        if not data.has_key('ID_FS_TYPE'):
            # we don't have a filesystem only a full device (ex: /dev/sda)
            if not data.has_key('ID_VENDOR'):
                vendor=""
            else:
                vendor=data['ID_VENDOR']
            if not data.has_key('ID_MODEL'):
                model=""
            else:
                model=data['ID_MODEL']
            if action == "add":
                self.show_notification( _("From terminal %(host)s.\nConnected Firewire device %(device)s\n%(vendor)s %(model)s" ) \
                %{"host":self.hostname, "device":device, "vendor":vendor, "model":model } )
            if action == "remove":
                self.show_notification( _("From terminal %(host)s.\nDisconnected Firewire device %(device)s\n%(vendor)s %(model)s" ) \
                %{"host":self.hostname, "device":device, "vendor":vendor, "model":model } ) 
            return
        
        else:
            # we have a filesystem ex: /dev/sda1
            if not data.has_key('ID_FS_TYPE'):
                fstype=""
            else:
                fstype=data['ID_FS_TYPE']
            
            if fstype == "swap" or fstype == "extended": return
            
            usb_status=self.xmlrpc.GetDevicesInfo(device=device, mode="--getstatus")
            if usb_status == "0":
                mount=True
                n=1
            else:
                mount=False
                n=2
            
            # add to menu
            devid=device.split('/')[2]
            remote_mnt="/mnt/%s" %(devid)
            if action == "add" or action == "mount":
                if action == "add":
                    ###########     add Firewire  device    ############
                    self.systray.register_device("usb_%s"%devid, 
                                    _("Firewire device %s") %devid, 
                                    "usb%s.png"%n, True, 
                                    {
                                "usb_%s_mount" %devid: [ _("Mount Firewire device %s") %(devid),  "usb_mount.png", mount,  None, device],
                                "usb_%s_umount" %devid: [ _("Umount Firewire device %s") %(devid), "usb_umount.png", not mount, None, device]
                                    }, 
                                    device)
                    
                    self.systray.register_action("usb_%s_mount" %devid , self.firewire, {
                                            "DEVNAME": device, "ACTION": "mount", "ID_FS_TYPE": fstype, "FORCE_MOUNT":True
                                                                                    } 
                                                )
                    self.systray.register_action("usb_%s_umount" %devid , self.firewire, {
                                            "DEVNAME": device, "ACTION": "umount", "ID_FS_TYPE": fstype, "FORCE_MOUNT":True
                                                                                    }
                                                 )
                    ###############################################
                    
                    if not self.mounter_remote(device, fstype, "--mount"):
                        self.show_notification (  _("Error, can't mount device %s") %(device)  )
                        return
                
                    if device in self.mounted:
                        data['ID_FS_LABEL']=os.path.basename(self.mounted[device])
                        data['ID_VENDOR']=os.path.basename(self.mounted[device])
                
                if action == "mount":
                    # mount from menu and wait for udev mount event
                    if data.has_key("FORCE_MOUNT") and data["FORCE_MOUNT"]:
                        if not self.mounter_remote(device, fstype, "--mount"):
                            self.show_notification (  _("Error, can't mount device %s") %(device)  )
                        return
                
                    # remote device is mounted, mount_local and launch filemanager
                    local_mount_point = self.get_local_mountpoint(data)
                    label = os.path.basename(local_mount_point)
                
                    # mount with fuse and ltspfs    
                    if not self.mounter_local(local_mount_point, remote_mnt, device=device, label=label, mode="mount"):
                        return
                
                    # launch desktop filemanager
                    self.launch_desktop_filemanager(local_mount_point)
                    self.mounted[device]=local_mount_point
                    ##########################################
                
                
            elif action == "remove" or action == "umount":
                if action == "remove":
                    print_debug ("firewire() UNREGISTER SERVICE")
                    self.systray.unregister_device("usb_%s"%devid)
                if device in self.mounted:
                    local_mount_point=self.mounted[device]
                    label = os.path.basename(local_mount_point)
                else:
                    print_debug ( "remove_firewire() device %s not found in self.mounted" %(device) )
                    return
                # umount local fuse
                # check if fuse is mounted
                status=self.common.exe_cmd("mount |grep -c %s" %(local_mount_point), verbose=1, background=False, lines=0, cthreads=0 )
                if int(status) != 0:
                    self.mounter_local(local_mount_point, remote_mnt, device=device, label=label, mode="umount")
                
                # umount remote device
                # check if remote is mounted (user can umount before from desktop icon)
                print_debug("firewire() GETSTATUS device =%s"%device)
                status=self.xmlrpc.GetDevicesInfo(device=device, mode="--getstatus")
                try:
                    status=int(status)
                    if status == 0:
                        print_debug ( "remove_firewire() device=%s seems not mounted" %(device) )
                        self.systray.update_status("usb_%s"%devid, "usb_%s_mount"%devid, True)
                        self.systray.update_status("usb_%s"%devid, "usb_%s_umount"%devid, False)
                        
                    else:
                        if not self.mounter_remote(device, fstype, "--umount"):
                            self.show_notification (  _("Error, can't mount device %s") %(device)  )
                            return
                except Exception, err:
                    print_debug ( "firewire() Exception error %s"%err )
        
    def update_cdrom_usb(self, devid, action=None):
        #print_debug ("update_cdrom_usb()")
        
        device="/dev/%s" %devid
        
        if action ==  "umount":
            self.show_notification (  _("CDROM USB device %s umounted. You can extract it.") %(devid)  )
            
        if action ==  "mount" or action ==  "add":
            self.show_notification (  _("CDROM USB device %s mounted. Ready for use.") %(devid)  )
        
        print_debug("update_cdrom_usb() GETSTATUS device=%s action=%s"%(device, action) )

        usb_status=self.xmlrpc.GetDevicesInfo(device, mode="--getstatus")
        if usb_status == "0":
            ismounted=False
            n=1
        else:
            ismounted=True
            n=2
        print_debug ("update_cdrom_usb() usb devid=%s ismounted=%s" %(devid, ismounted) )
        #self.systray.items["usb_"%devid][1]="usb%s.png"%n
        self.systray.update_status("usb_%s"%devid, "usb_%s_mount"%devid, not ismounted)
        self.systray.update_status("usb_%s"%devid, "usb_%s_umount"%devid, ismounted)


    def update_usb(self, *args):
        #print_debug ("update_usb()")
        data=args[0]
        action=data['ACTION']
        
        if not data.has_key("ID_FS_TYPE"):
            # don't update if we have disk (only partititions)
            return
        
        if data["ID_FS_TYPE"] == "" or data["ID_FS_TYPE"] == "swap" or data["ID_FS_TYPE"] == "extended":
            # don't update if fstype is empty (devicesctl.sh and udev put FILESYSTEM always)
            return
        
        device="/dev/%s" %data['DEVPATH'].split('/')[2]
        
        if( len( data['DEVPATH'].split('/') ) ) > 3:
            devid=data['DEVPATH'].split('/')[3]
        else:
            devid=data['DEVPATH'].split('/')[2]
        
        if action ==  "umount":
            self.show_notification (  _("USB device %s umounted. You can extract it.") %(devid)  )
            
        if action ==  "mount":
            self.show_notification (  _("USB device %s mounted. Ready for use.") %(devid)  )
        
        print_debug("update_usb() GETSTATUS device=%s data=%s"%(device, data) )
        usb_status=self.xmlrpc.GetDevicesInfo(data['DEVNAME'], mode="--getstatus")
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
        
    def update_firewire(self, *args):
        #print_debug ("update_firewire()")
        data=args[0]
        action=data['ACTION']
        
        if not data.has_key("ID_FS_TYPE"):
            # don't update if we have disk (only partititions)
            return
        
        if data["ID_FS_TYPE"] == "" or data["ID_FS_TYPE"] == "swap" or data["ID_FS_TYPE"] == "extended":
            # don't update if fstype is empty (devicesctl.sh and udev put FILESYSTEM always)
            return
        
        device="/dev/%s" %data['DEVPATH'].split('/')[2]
        
        if( len( data['DEVPATH'].split('/') ) ) > 3:
            devid=data['DEVPATH'].split('/')[3]
        else:
            devid=data['DEVPATH'].split('/')[2]
        
        if action ==  "umount":
            self.show_notification (  _("Firewire device %s umounted. You can extract it.") %(devid)  )
            
        if action ==  "mount":
            self.show_notification (  _("Firewire device %s mounted. Ready for use.") %(devid)  )
        
        print_debug("update_firewire() GETSTATUS device=%s data=%s"%(device, data) )
        usb_status=self.xmlrpc.GetDevicesInfo(data['DEVNAME'], mode="--getstatus")
        if usb_status == "0":
            ismounted=False
            n=1
        else:
            ismounted=True
            n=2
        print_debug ("update_firewire() usb devid=%s ismounted=%s" %(devid, ismounted) )
        #self.systray.items["usb_"%devid][1]="usb%s.png"%n
        self.systray.update_status("usb_%s"%devid, "usb_%s_mount"%devid, not ismounted)
        self.systray.update_status("usb_%s"%devid, "usb_%s_umount"%devid, ismounted)
        
    def remove_dupes(self, mylist):
        """
        check for duplicate events, 
        kernel sometimes create 3-4 umount events before mounting a device
        the events are created and diff at max 1 second
        """
        if len(mylist) != 1:
            have_umount=False
            have_mount=False
            umount_index=None
            nodupes=[]
            try:
                nodupes=list(set(mylist))
            except:
                pass
            
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
        is_gnome=self.common.exe_cmd("ps ux |grep gnome-panel  |grep -c -v grep", verbose=1, background=False, lines=0, cthreads=0  )
        is_kde = self.common.exe_cmd("ps ux |grep -e startkde -e kwin |grep -c -v grep", verbose=1, background=False, lines=0, cthreads=0  )
        is_xfce= self.common.exe_cmd("ps ux |grep xfce4-panel  |grep -c -v grep", verbose=1, background=False, lines=0, cthreads=0  )
        try:
            if int(is_gnome) > 0:
                return "gnome"
            elif int(is_kde) > 0:
                return "kde"
            elif int(is_xfce) > 0:
                return "xfce4"
        except Exception, e:
            print_debug("Can't read desktop type, error: %s"%e)
            return ""

    def launch_desktop_filemanager(self, path=""):
        if self.desktop == "gnome":
            cmd="nautilus %s" %(path)
        elif self.desktop == "kde":
            if os.path.isfile("/usr/bin/dolphin"):
                cmd="dolphin %s" %(path)
            else:
                cmd="konqueror %s" %(path)
        elif self.desktop == "xfce4":
            cmd="Thunar %s" %(path)
        else:
            print_debug (  "launch_desktop_filemanager() unknow desktop, not launching filemanager" )
            return
        # exe filemanager in a new thread to not freeze status icon
        filemanager=threading.Thread(target=self.exec_filemanager, args=[cmd] )
        filemanager.start()
        return

    def exec_filemanager(self, *args):
        print_debug("exec_filemanager() args='%s'" %(args[0]) )
        self.common.exe_cmd(args[0], verbose=1, background=False, lines=0, cthreads=0 )

    def umount_all(self):
        mounted=self.common.exe_cmd("grep ^ltspfs /proc/mounts |grep -e \"user_id=%s\" -e \"user=%s\" | awk '{print $2}'" %(os.getuid(),  pwd.getpwuid(os.getuid())[0]), verbose=1, background=False, lines=0, cthreads=0 )
        if isinstance(mounted, str):
            mounted=[mounted]
        for mount in mounted:
            print_debug( "umount_all() umounting %s..." %mount )
            self.common.exe_cmd("fusermount -u %s 2>&1" %mount, verbose=1, background=False, lines=0, cthreads=0)
            self.common.exe_cmd("fusermount -uz %s 2>/dev/null" %mount, verbose=1, background=False, lines=0, cthreads=0)
            # delete dir
            try:
                os.rmdir(mount)
            except Exception, err:
                print_debug("umount_all() Exception, error %s"%err)
          
    def exit(self):
        # say udev_daemon loop to quit
        self.quitting=True
        self.umount_all()
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
            if app.desktop == "": app.desktop=app.get_desktop()
            app.udev_daemon()
            time.sleep(3)
        except KeyboardInterrupt:
            print ("Get KeyboardInterrupt (udev loop), existing...")
            app.quitting=True
            app.mainloop.quit()
            break
        
    # join gui thread    
    tcosdevices.join()
    sys.exit(0)
    
