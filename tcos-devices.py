#!/usr/bin/env python2.4
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


"""

udev env vars

ID_BUS=usb
UDEV_LOG=0
DEVNAME=/dev/sda1
ACTION=remove
ID_FS_LABEL_SAFE=USB-LIVE
SEQNUM=1588
ID_TYPE=disk
MAJOR=8
ID_FS_UUID=9422-105B
DEVPATH=/block/sda/sda1
ID_FS_LABEL=USB-LIVE
ID_FS_VERSION=FAT32
ID_MODEL=TS128MJF2A
DEVLINKS=/dev/disk/by-id/usb-JetFlash_TS128MJF2A_0401081008480-part1 /dev/disk/by-path/pci-0000:00:07.2-usb-0:1:1.0-scsi-0:0:0:0-part1 /dev/disk/by-uuid/9422-105B /dev/disk/by-label/USB-LIVE
ID_SERIAL=JetFlash_TS128MJF2A_0401081008480
SUBSYSTEM=block
PATH=/usr/local/bin:/usr/bin:/sbin:/bin
PHYSDEVPATH=/devices/pci0000:00/0000:00:07.2/usb1/1-1/1-1:1.0/host5/target5:0:0/5:0:0:0
MINOR=1
ID_FS_TYPE=vfat
PHYSDEVDRIVER=sd
ID_PATH=pci-0000:00:07.2-usb-0:1:1.0-scsi-0:0:0:0
PWD=/
ID_VENDOR=JetFlash
UDEVD_EVENT=1
PHYSDEVBUS=scsi
ID_FS_USAGE=filesystem
ID_REVISION=1.00


"""


import os, sys
import gobject
import getopt
from gettext import gettext as _


if not os.path.isfile("shared.py"):
        sys.path.append('/usr/share/tcosmonitor')
else:
        sys.path.append('./')



import shared
# load conf file and exit if not active
if not shared.test_start("tcos-devices") :
    print "tcos-devices disabled at %s" %(shared.module_conf_file)
    sys.exit(1)

import pygtk
pygtk.require('2.0')
from gtk import *
import gtk.glade

#import pygtk
#pygtk.require('2.0')
#from gtk import *
#import gtk.glade
import pynotify
import pwd


def print_debug(txt):
    if shared.debug:
        print "%s::%s" %("tcos-devices", txt)

def get_username():
    return pwd.getpwuid(os.getuid())[0]


def usage():
    print "tcos-devices help:"
    print ""
    print "   tcos-devices [--host=XXX.XXX.XXX.XXX] "
    print "                 (force host to connect to reach devices, default is DISPLAY)"
    print "   tcos-devices --daemon      (run as daemon to scan dmesg output)"
    print "   tcos-devices -d [--debug]  (write debug data to stdout)"
    print "   tcos-devices -h [--help]   (this help)"


try:
    opts, args = getopt.getopt(sys.argv[1:], ":hd", ["help", "hidden", "debug", "daemon" ,"host=", "umount" , "local=", "remote="])
except getopt.error, msg:
    print msg
    print "for command line options use tcos-devices --help"
    sys.exit(2)

shared.remotehost, display =  os.environ["DISPLAY"].split(':')
shared.run_as_daemon=False
shared.hidden_window=False
action = ""

# process options
for o, a in opts:
    if o in ("-d", "--debug"):
        shared.debug = True
    if o == "--host":
        shared.remotehost = a
    if o in ("-h", "--help"):
        usage()
        sys.exit()
    if o in ("--daemon"):
        shared.run_as_daemon=True
        
    if o in ("--hidden"):
        shared.hidden_window=True
            
    if o == "--umount":
        action = "umount"
    if o == "--remote":
        remote_mnt=a
    if o == "--local":
        local_mnt=a

if shared.remotehost == "":
    print "tcos-devices: Not allowed to run in local DISPLAY"
    #shared.error_msg ( _("tcos-devices isn't allowed to run in local DISPLAY\nForce with --host=xx.xx.xx.xx") )
    sys.exit(0)


def print_debug(txt):
    if shared.debug:
        print "%s::%s" %("tcos-devices", txt)
    return
        

class TcosDevices:
    def __init__(self, host):
        self.host=host
        self.name="TcosDevices"
        self.mounted={}
        self.username=get_username()
        
        if not self.is_in_group("fuse"):
            print _("Your user isn't in fuse group, ask your system administrator.")
            sys.exit(0)
        
        from ping import PingPort
        if PingPort(self.host, shared.xmlremote_port, 0.5).get_status() != "OPEN":
            print _("ERROR: It appears that TcosXmlRpc is not running on %s.") %(self.host)
            #shared.error_msg( _("ERROR: It appears that TcosXmlRpc is not running on %s.") %(self.host) )
            sys.exit(1)
            
        
        self.desktop=self.get_desktop()
        print_debug ( "__init__ current desktop: %s" %(self.desktop) )
        
        
        # get all devices
        import TcosXmlRpc
        import TcosConf
        import TcosXauth
        self.xauth=TcosXauth.TcosXauth(self)
        self.xauth.init_standalone()
        print_debug ( "tcos-devices:: loading config class..." )
        self.config=TcosConf.TcosConf(self, openfile=False)
        self.xmlrpc=TcosXmlRpc.TcosXmlRpc(self)
        
        # make a test and exit if no cookie match
        if not self.xauth.test_auth():
            print "tcos-devices: ERROR: Xauth cookie don't match"
            #sys.exit(1)
        
        
        self.xmlrpc.newhost(self.host)
        if not self.xmlrpc.connected:
            print _("Error connecting with TcosXmlRpc in %s.") %(self.host)
            #shared.error_msg( _("Error connecting with TcosXmlRpc in %s.") %(self.host) )
            sys.exit(1)
    
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
    
    def get_local_mountpoint(self, line):
        print_debug( line )
        desktop=os.path.expanduser("~/Desktop")
        data=line.split('#')
        #fslabel=data[4].split('=')[1]
        #fsvendor=data[6].split('=')[1]
        fslabel=self.get_value(data, "ID_FS_LABEL")
        fsvendor=self.get_value(data, "ID_VENDOR")
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
                        print_debug ( "remove_dupes() Deleting umount ACTION: %s" %nodupes[i] )
                        del nodupes[i]
                        break
            mylist=nodupes
        return mylist
    
    def init_daemon(self):
        # two list, first contain a part of dmesg line
        # second contains function to exec with line arg
        #
        # id_bus=$(get_env_var "ID_BUS")
        # device=$(get_env_var "DEVNAME")
        # action=$(get_env_var "ACTION")
        # label=$(get_env_var "ID_FS_LABEL")
        # fs_type=$(get_env_var "ID_FS_TYPE")
        # vendor=$(get_env_var "ID_VENDOR")
        # model=$(get_env_var "ID_MODEL")
        # devpath=$(get_env_var "DEVPATH")
        #
        # echo "$id_bus#$device#$action#$label#$fs_type#$vendor#$model#$devpath" >> $output_file
        #
        print_debug ("init_daemon() running as daemon...")
        from time import sleep
        
        """ listen is a udev event dictionary
            key is a string like "mount" or "insert", not very important
            value is a list:
              * list[0] is another list with all udev conditions, example: ["ID_BUS=usb", "ACTION=add"]
              * list[1] is python function to do, example: self.mount_floppy_event
        """
        listen={ 
        "insert":[ ["ID_BUS=usb", "ACTION=add"],    self.add_usb], 
        "remove":[ ["ID_BUS=usb", "ACTION=remove"], self.remove_usb], 
        "mount-floppy":[ ["DEVPATH=/block/fd0", "ACTION=mount"] , self.mount_floppy_event ],
        "umount-floppy":[ ["DEVPATH=/block/fd0", "ACTION=umount"], self.umount_floppy_event ],
        "mount-cdrom":[ ["DEVPATH=/block/hd", "ACTION=mount"] , self.mount_cdrom_event ],
        "umount-cdrom":[ ["DEVPATH=/block/hd", "ACTION=umount"], self.umount_cdrom_event ], 
        "mount-flash":[ ["DEVPATH=/block/sd", "ACTION=mount"] , self.mount_flash_event ],
        "umount-flash":[ ["DEVPATH=/block/sd", "ACTION=umount"], self.umount_flash_event ]
        }
        
        udev_old=""
        first_run=True
        self.worker_running=False
        try:
            while True:
                udev=self.xmlrpc.GetDevicesInfo(device="", mode="--getudev").split('|')
                if "error" in " ".join(udev):
                    print "tcos-devices: Connection error: \"%s\" ..." %( " ".join(udev) )
                    continue
                    # dont exit
                    #sys.exit(1)
                print_debug ( "action udev=%s" %(udev) )
                
                # remove last
                udev=udev[:-1]
                
                if udev != udev_old and udev[0] != "unknow":
                    # delete duplicate events
                    udev=self.remove_dupes(udev)
                    ################################
                    for line in udev:
                        ######################
                        self.action_found=True
                        for event in listen:
                            #print_debug ( "EVENT=%s value=%s" %(event, listen[event]) )
                            # check for all events
                            for udev_var in listen[event][0]:
                                if not udev_var in line:
                                    #print_debug ( "***BREAK, udev_var=%s not found in line=%s" %(udev_var, line) )
                                    self.action_found=False
                                    break
                                else:
                                    #print_debug ( "***PASS, udev_var=%s found !!!" %(udev_var) )
                                    self.action_found=True
                                    
                            if self.action_found:
                                #print_debug ( "##EVENT MATCH## exec=%s args=%s" %(listen[event][1] , ([line])) )
                                # if here we have all events
                                self.worker_running=False
                                worker=shared.Workers(self, target=listen[event][1], args=([line]), dog=False)
                                worker.start()
                            #else:
                            #    print_debug ( "##EVENT NOT MATCH##" )
                            
                        ###################### OLD CODE ################
                        #for event in events:
                        #    if event[0] in line and event[1] in line:
                        #        function_call=actions[events.index(event)]
                        #        #function_call( line )
                        #        self.worker_running=False
                        #        worker=shared.Workers(self, target=function_call, args=([line]), dog=False)
                        #        worker.start()
                                
                        
                udev_old=udev       
                sleep(3) # time between scan udev events
                first_run=False
                # check if desktop is running, else, quit....
                if self.desktop != self.get_desktop():
                    print_debug( "init_daemon() desktop has gone, exit..." )
                    sys.exit(0)
        except KeyboardInterrupt: # Por si se pulsa Ctrl+C
            print_debug ( "init_daemon() Ctrl+C exiting...." )
            sys.exit(0)
    
    def get_value(self, data, key):
        """
           returns value of given key, example:
              data=["ID_BUS=usb", "DEVICE=/dev/sda", "FSTYPE=vfat"]
              if key="DEVICE"
                returns "/dev/sda" 
            udev current avalaible keys:
             "ID_BUS" "DEVNAME" "ACTION" "ID_FS_LABEL" "ID_FS_TYPE" "ID_VENDOR" "ID_MODEL" "DEVPATH"
        """
        print_debug ( "::==> get_value() searching for \"%s\"" %key )
        for uvar in data:
            if uvar.split('=')[0] == key:
                print_debug ( "::==> get_value() FOUND key=%s value=%s" %(key, uvar.split('=')[1]) )
                return uvar.split('=')[1]
        # return empty string if not found
        return ""
    
    def mount_floppy_event(self, line):
        self.show_notification (  _("Floppy mounted. Ready for use.")  )
    
    def umount_floppy_event(self, line):
        self.show_notification (  _("Floppy umounted. You can extract it.")  )
    
    def mount_cdrom_event(self,line):
        self.show_notification (  _("Cdrom mounted. Ready for use.")  )
        
    def umount_cdrom_event(self, line):
        self.show_notification (  _("Cdrom umounted. You can extract it.")  )
        print_debug ( "umount_cdrom_event() line=%s" %(line) )
        data=line.split('#')
        device=self.get_value(data, "DEVPATH").split("/")[2]
        print_debug("umount_cdrom_event()  EJECT device %s" %(device) )
        self.xmlrpc.GetDevicesInfo(device=device, mode="--eject")

    def mount_flash_event(self, line):
        self.show_notification (  _("Flash device mounted. Ready for use.")  )
    
    def umount_flash_event(self, line):
        self.show_notification (  _("Flash device umounted. You can extract it.")  )
    
    def add_usb(self, line):
        data=line.split('#')
        print_debug ( "add_usb() data=%s" %data )
        
        device=self.get_value(data, "DEVNAME")
        fstype=self.get_value(data, "ID_FS_TYPE")
        #device=data[1].split('=')[1]
        #fstype=data[4]
        
        # /dev/sda
        #if len(device) < 9:
        if fstype == "":
            vendor=self.get_value(data, "ID_VENDOR")
            model=self.get_value(data, "ID_MODEL")
            #vendor=data[5].split('=')[1]
            #model=data[6].split('=')[1]
            # this is a disk, search a partition
            self.show_notification( _("From terminal %(host)s.\nConnected USB device %(device)s\n%(vendor)s %(model)s" ) \
         %{"host":shared.remotehost, "device":device, "vendor":vendor, "model":model } ) 
            return
        
        # we have something like /dev/sda1
        #fstype=data[4].split('=')[1]
        if not self.mounter_remote(device, fstype, "--mount"):
            self.show_notification (  _("Can't mount device %s") %(device)  )
            return
            
        
        remote_mnt="/mnt/%s" %(device[5:])
        local_mount_point = self.get_local_mountpoint(line)
        label = os.path.basename(local_mount_point)
        
        # mount with fuse and ltspfs    
        self.mounter_local(local_mount_point, remote_mnt, device=device, label=label, mode="mount")
        
        # launch desktop filemanager
        self.launch_desktop_filemanager(local_mount_point)
        
        self.mounted[device]=local_mount_point
        
        print_debug ( "add_usb() self.mounted=%s" %(self.mounted) )
        print_debug ( "add_usb() ADD usb, done...")

    def remove_usb(self, line):
        data=line.split('#')
        print_debug ( "remove_usb() data=%s" %data )
        
        device=self.get_value(data, "DEVNAME")
        fstype=self.get_value(data, "ID_FS_TYPE")
        #device=data[2].split('=')[1]
        # /dev/sda
        #fstype=data[5]
        
        # /dev/sda
        #if len(device) < 9:
        if fstype == "":
            vendor=self.get_value(data, "ID_VENDOR")
            model=self.get_value(data, "ID_MODEL")
            #vendor=data[6].split('=')[1]
            #model=data[7].split('=')[1]
            # this is a disk, search a partition
            self.show_notification( _("From terminal %(host)s.\nDisconnected USB device %(device)s\n%(vendor)s %(model)s" ) \
         %{"host":shared.remotehost, "device":device, "vendor":vendor, "model":model } ) 
            return
        
        # here we have something like this /dev/sda1
        # umount local
        
        remote_mnt="/mnt/%s" %(device[5:])
        
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
                #fstype=data[5].split('=')[1]
                if not self.mounter_remote(device, fstype, "--umount"):
                    self.show_notification (  _("Can't umount device %s") %(device)  )
                    return
        except ValueError:
            print_debug ( "error loading device status" )
        
        
        if device in self.mounted:
            del self.mounted[device]
        else:
            print_debug ( "remove_usb() devive=%s not in self.mounted dictionary" )
        
        print_debug ( "remove_usb() self.mounted=%s" %(self.mounted) )   
        print_debug ( "remove_usb() REMOVE usb, done" )
    
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
            # create icon
            icon_filename=os.path.join(local_mount_point + ".desktop")
            icon_data="""[Desktop Entry]
Version=1.0
Encoding=UTF-8
Name=%s
Exec=tcos-devices --umount --local="%s" --remote="%s" --host=%s
Terminal=false
Type=Application
Icon=/usr/share/pixmaps/tcos-icon-32x32.png
Categories=GNOME;Application

                """ %(_("Umount %s remote device") %(label), local_mount_point, device, shared.remotehost)
            fd=file(icon_filename, 'w')
            fd.write(icon_data)
            fd.close
            # send notification
            self.show_notification( _("Mounting device %(device)s in \n%(mnt_point)s\nPlease wait...\nClick on Desktop icon to secure umount." )\
             %{"device":device, "mnt_point":local_mount_point}, urgency=pynotify.URGENCY_NORMAL )
        
        if mode == "umount":
            if os.path.isdir(local_mount_point):
                print_debug ( "mounter_local() umounting %s" %(local_mount_point) )
                self.exe_cmd("fusermount -u %s" %(local_mount_point) )
                print_debug ( "mounter_local() removing dir %s" %(local_mount_point) )
                os.rmdir(local_mount_point)
            # delete umount icon if exists
            if os.path.isfile(os.path.join(local_mount_point + ".desktop")):
                os.remove(os.path.join(local_mount_point + ".desktop"))
            
            mydevice=""
            for dev in self.mounted:
                if local_mount_point == self.mounted[dev]:
                    mydevice=device
                
            self.show_notification( _("Umounting device %s.\nPlease wait..." ) %(mydevice)\
             , urgency=pynotify.URGENCY_NORMAL )
            
    
    def is_in_group(self, group=""):
        groups=self.exe_cmd("id")
        if group != "":
            if group in groups: return True
            else: return False
    
    def launch_desktop_filemanager(self, path=""):
        if self.desktop == "gnome":
            os.system("nautilus %s" %(path) )
        elif self.desktop == "kde":
            os.system("konqueror %s" %(path) )
        elif self.desktop == "xfce4":
            os.system("Thunar %s" %(path) )
        else:
            print_debug (  "launch_desktop_filemanager() unknow desktop, not launching filemanager" )
            
    def show_notification(self, msg, urgency=pynotify.URGENCY_CRITICAL):
        pynotify.init("Multi Action Test")
        n = pynotify.Notification( _("Tcos device daemon") , msg )
        n.set_urgency(urgency)
        n.set_category("device")
        n.set_timeout(15000) # 15 sec
        if not n.show():
            print_debug  ("show_notification() Failed to send notification")
        
  
    def init_gui(self):
        # check if running, only one per user
        status=self.exe_cmd("ps ux |grep \"tcos-devices --hidden\"|grep -c -v grep" )
        if int(status) > 1:
            print "tcos-devices: another process is running..."
            sys.exit(0)
        
        # based on http://www.burtonini.com/computing/notify.py
        import egg.trayicon
        icon = egg.trayicon.TrayIcon("TCOS")
        eventbox = gtk.EventBox()
        icon.add(eventbox)
        #tcos-icon-32x32.png
        image=gtk.Image()
        image.set_from_file (shared.IMG_DIR + "tcos-icon-32x32.png")
        eventbox.add(image)
        tips = gtk.Tooltips()

        # http://www.daa.com.au/pipermail/pygtk/2005-August/010790.html

        tips.set_tip(icon, ( _("Tcos Devices daemon on host %s") %(self.host) )[0:79])
        tips.enable()
        icon.show_all()
        eventbox.connect("button_press_event",
                         self.on_tray_icon_press_event)
        
        #import shared
        gtk.glade.bindtextdomain(shared.PACKAGE, shared.LOCALE_DIR)
        gtk.glade.textdomain(shared.PACKAGE)
        
        # Widgets
        self.ui = gtk.glade.XML(shared.GLADE_DIR + 'tcos-devices.glade')
        self.mainwindow = self.ui.get_widget('mainwindow')
        
        # close windows signals
        self.mainwindow.connect('delete-event', self.hide_mainwindow )
        self.mainwindow.hide()
        
        
        
        
        self.mainwindow.set_icon_from_file(shared.IMG_DIR + 'tcos-icon-32x32.png')
        self.mainwindow.set_title( _("Tcos Devices on %s host") %(self.host)  )
        self.mainwindow.hide()
        
        self.quit_button=self.ui.get_widget('quit_button')
        self.quit_button.connect("clicked", self.salirse)
        self.refresh_button=self.ui.get_widget('refresh_button')
        self.refresh_button.connect("clicked", self.get_data)
        
        self.hide_button=self.ui.get_widget('hide_button')
        self.hide_button.connect("clicked", self.hide_mainwindow)
        
        self.floppy_label=self.ui.get_widget('floppy_label')
        self.cdrom_label=self.ui.get_widget('cdrom_label')
        
        self.floppy_mount_button=self.ui.get_widget('floppy_mount')
        self.floppy_umount_button=self.ui.get_widget('floppy_umount')
        self.cdrom_mount_button=self.ui.get_widget('cdrom_mount')
        self.cdrom_umount_button=self.ui.get_widget('cdrom_umount')
    
        # connect signals
        self.floppy_mount_button.connect("clicked", self.floppy_mount)
        self.floppy_umount_button.connect("clicked", self.floppy_umount)
        self.cdrom_mount_button.connect("clicked", self.cdrom_mount)
        self.cdrom_umount_button.connect("clicked", self.cdrom_umount)
        
        # get data from host
        self.get_data()
        
        # show main window if not hidden defined
        if not shared.hidden_window:
            self.mainwindow.show()
    
    def get_data(self, *args):
        # get status of devices
        self.floppy_status=self.xmlrpc.GetDevicesInfo(device="/dev/fd0", mode="--getstatus").replace('\n','')
        try:
            self.floppy_status=int(self.floppy_status)
            if self.floppy_status == 0:
                self.update_floppy_status(False)
            else:
                self.update_floppy_status(True)
        except ValueError:
            print_debug ( "error loading floppy status" )
            self.update_floppy_status(False)
        
        # get a list of cdrom devices, and choose first device
        self.cdrom_device=None    
        self.cdrom_devices=self.xmlrpc.GetDevicesInfo(device="", mode="--getcdrom").split('|')
        print_debug ( "get_data() cdroms=%s" %(self.cdrom_devices) )
        self.cdrom_devices=self.cdrom_devices[0:-1]
        print_debug ( "get_data() detected cdroms=%s" %self.cdrom_devices )
        if len(self.cdrom_devices) > 0:
            print_debug (  _("No support for more than one cdrom, first detected will be used")  )
            self.cdrom_device="/dev/" + self.cdrom_devices[0]
            self.cdrom_remote="/mnt/" + self.cdrom_devices[0]
        elif len(self.cdrom_devices) == 0:
            #self.show_notification (  _("No cdrom detected. Click on refresh button.")  )
            self.cdrom_mount_button.set_sensitive(False)
            self.cdrom_umount_button.set_sensitive(False)
        
        self.cdrom_status= self.xmlrpc.GetDevicesInfo(device=self.cdrom_device, mode="--getstatus").replace('\n','')
        try:
            self.cdrom_status=int(self.cdrom_status)
            if self.cdrom_status == 0:
                print_debug ( "cdrom_status not mounted %d" %self.cdrom_status )
                self.update_cdrom_status(False)
            elif self.cdrom_status > 0:
                self.update_cdrom_status(True)
                print_debug ( "cdrom_status mounted %d" %self.cdrom_status )
        except ValueError:
            print_debug ( "error loading cdrom status" )
            self.cdrom_mount_button.set_sensitive(False)
            self.cdrom_umount_button.set_sensitive(False)
        
        print_debug ( "get_data()  cdrom_device=%s" %(self.cdrom_device) )
    
    def floppy_mount(self, widget):
        desktop=os.path.expanduser("~/Desktop")
        local_mount_point=os.path.join(desktop, _("Floppy") )
        
        if not self.mounter_remote("/dev/fd0", "", mode="--mount"):
            self.show_notification (  _("Can't mount floppy")  )
            return
        self.mounter_local(local_mount_point, "/mnt/fd0", device="/dev/fd0", label=_("Floppy"), mode="mount")
        
        # change status
        self.update_floppy_status(True)
        self.launch_desktop_filemanager(local_mount_point)
        return
        
    def floppy_umount(self, widget):
        desktop=os.path.expanduser("~/Desktop")
        local_mount_point=os.path.join(desktop, _("Floppy") )
        
        self.mounter_local(local_mount_point, "/mnt/fd0", device="/dev/fd0", label=_("Floppy"), mode="umount")
        
        if not self.mounter_remote("/dev/fd0", "", mode="--umount"):
            self.show_notification (  _("Can't umount floppy")  )
            return
        
        # change status
        self.update_floppy_status(False)
        return
        
    def cdrom_mount(self, widget):
        desktop=os.path.expanduser("~/Desktop")
        local_mount_point=os.path.join(desktop, _("Cdrom") )
        
        if not self.mounter_remote(self.cdrom_device, "", mode="--mount"):
            self.show_notification (  _("Can't mount cdrom")  )
            return
        self.mounter_local(local_mount_point, self.cdrom_remote, device=self.cdrom_device, label=_("Cdrom"), mode="mount")
        
        # change status
        self.update_cdrom_status(True)
        self.launch_desktop_filemanager(local_mount_point)
        return
        
    def cdrom_umount(self, widget):
        desktop=os.path.expanduser("~/Desktop")
        local_mount_point=os.path.join(desktop, _("Cdrom") )
        
        print_debug ( "cdrom_umount() remote_mnt=%s device=%s" %(self.cdrom_remote, self.cdrom_device) )
        
        self.mounter_local(local_mount_point, self.cdrom_remote, device=self.cdrom_device, label=_("Cdrom"), mode="umount")
        
        if not self.mounter_remote(self.cdrom_device, "", mode="--umount"):
            self.show_notification (  _("Can't umount cdrom")  )
            return
        
        # change status
        self.update_cdrom_status(False)
        return
    
    def update_floppy_status(self, value):
        self.floppy_status=value
        self.floppy_mount_button.set_sensitive(not value)
        self.floppy_umount_button.set_sensitive(value)
    
    def update_cdrom_status(self, value):
        print_debug ( "update_cdrom_status() set to " + str(value) )
        self.cdrom_status=value
        self.cdrom_mount_button.set_sensitive(not value)
        self.cdrom_umount_button.set_sensitive(value)
        
    def on_tray_icon_press_event(self, widget, event):
        self.mainwindow.show()
        return
        """
        print "tray event"
        time=event.time
        # show a menu
        
        menu_list=[
        [_("Show avalaible devices"), None, 1]
        ]
        
        self.traymenu=gtk.Menu()
        for element in menu_list:
            if element[1] != None and os.path.isfile(shared.IMG_DIR + element[1]):
                menu_items=gtk.ImageMenuItem(element[0], True)
                icon = gtk.Image()
                icon.set_from_file(shared.IMG_DIR + element[1])
                menu_items.set_image(icon)
            else:
                menu_items = gtk.MenuItem(element[0])
                self.traymenu.append(menu_items)
              
            menu_items.connect("activate", self.on_tray_rightclick, element[2])
            menu_items.show()
        self.traymenu.show_all()
        self.traymenu.popup( None, None, None, event.button, time)
        
    
    def on_tray_rightclick(self, menu_item, index):
        print "index=%d"  %index
        if index == 1:
            self.mainwindow.show()
    """
    
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


    def write_into_statusbar(self, msg, *args):
        context_id=self.statusbar.get_context_id("status")
        self.statusbar.pop(context_id)
        self.statusbar.push(context_id, msg)
        return False

    def hide_mainwindow(self, *args):
        self.mainwindow.hide()
        return True

    def salirse(self,True, *args):
        print_debug ( _("Exiting") )
        self.mainloop.quit()
        

    def run (self):
        self.mainloop = gobject.MainLoop()
        try:
            self.mainloop.run()
        except KeyboardInterrupt: # Por si se pulsa Ctrl+C
            self.salirse(True)

if __name__ == "__main__":
    if action == "umount":
        # umount "remote_mnt" in local and then in remote
        app=TcosDevices(shared.remotehost)
        app.show_notification( _("Umounting %s, please wait...") %(local_mnt) )
        app.mounter_local( local_mnt , remote_mnt, mode="umount")
        app.mounter_remote(remote_mnt, "", mode="--umount")
        sys.exit(0)
        
    if shared.run_as_daemon:
        app=TcosDevices(shared.remotehost)
        app.init_daemon()
    else:
        app=TcosDevices(shared.remotehost)
        app.init_gui()
        app.run()
