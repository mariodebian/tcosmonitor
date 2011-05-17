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

import pwd
import os
import time
import datetime
import gzip

import dbus
import dateutil.parser

CK_PATH="/var/log/ConsoleKit/"


def username(uid):
    try:
        return pwd.getpwuid( int(uid) ).pw_name
    except Exception, err:
        return None

class Connection(object):
    def __repr__(self):
        return "<Connection '%s': %s>"%(self.session_x11_display, str(self.__dict__))
    
    def __init__(self, line):
        self.type=None
        self.seat_id=None
        self.session_type=None
        self.session_remote_host_name=None
        self.session_unix_user=None
        self.username=None
        self.session_creation_time=None
        self.session_x11_display=None
        self.time=None
        self.strtime=None
        self.diffint=0
        self.__parse__(line)
        if self.session_unix_user:
            self.username=username(self.session_unix_user)
        if self.session_x11_display:
            self.session_x11_display=self.session_x11_display.replace("'", "")
        self.diff=self.diffnow()

    def __parse__(self, line):
        for elem in line.split():
            if not "=" in elem and "." in elem:
                self.strtime=elem
                self.time=time.localtime( float(elem) )
                continue
            if not "=" in elem: continue
            #print elem
            varname=elem.split('=')[0].replace('-', '_')
            value=elem.split('=')[1]
            if hasattr(self, varname):
                setattr(self, varname, value)

    def diffnow(self):
        diff=datetime.timedelta(0, time.time() - float(self.strtime))
        """
        >>> d = timedelta(microseconds=-1)
        >>> (d.days, d.seconds, d.microseconds)
        (-1, 86399, 999999)
        """
        self.diffint=int(diff.days)*86400 + int(diff.seconds)
        if diff.days > 0:
            return "%dd %s"%(diff.days, datetime.timedelta(0, diff.seconds))
        else:
            return "%s"%datetime.timedelta(0, diff.seconds)



class ConsoleKitHistory(object):
    def __init__(self, username=None, last=False):
        self.logfiles=[]
        self.data=[]
        self.searchlogs()
        # reverse logs
        #self.logfiles.reverse()
        #print self.logfiles
        self.readlogs()
        if username:
            newdata=[]
            for con in self.data:
                if con.username == username:
                    newdata.append(con)
            self.data=newdata
          
        # sort array by diffint
        self.data=sorted(self.data, key=lambda data: data.diffint)

        if last and len(self.data)>0:
            newdata=[self.data[0]]
            self.data=newdata

    def readlogs(self):
        for logfile in self.logfiles:
            if ".gz" in logfile:
                f = gzip.open(logfile, 'rb')
            else:
                f=open(logfile, 'r')
            for line in f.readlines():
                if "type=SEAT_SESSION_ADDED" in line:
                    con=Connection(line)
                    if con.username and int(con.session_unix_user) > 500 and con.session_x11_display != '' :
                        self.data.append( con )
            f.close()

    def searchlogs(self):
        if os.path.isfile(CK_PATH + "history"):
            self.logfiles.append(CK_PATH + "history")
        i=1
        if os.path.isfile(CK_PATH + "history" + "." + str(i)):
            self.logfiles.append(CK_PATH + "history" + "." + str(i))
        for i in range(2,10):
            if os.path.isfile(CK_PATH + "history" + "." + str(i) + ".gz"):
                self.logfiles.append(CK_PATH + "history" + "." + str(i) + ".gz")


class Display(object):
    def __repr__(self):
        return "<Display '%s': %s>"%(self.x11_display, str(self.__dict__))

    def __init__(self, obj):
        self.id=None
        self.seatid=None
        self.active=False
        self.is_local=None

        self.remote_host_name=None
        self.x11_display=None

        self.unix_user=None
        self.user=None
        self.__parse__(obj)

    def __parse__(self, obj):
        self.id=str(obj.GetId())
        self.seatid=str(obj.GetSeatId())

        self.is_local=bool(obj.IsLocal())

        self.remote_host_name=str(obj.GetRemoteHostname())
        self.x11_display=str(obj.GetX11DisplayName())


        bus = dbus.SystemBus ()
        manager_obj = bus.get_object ('org.freedesktop.ConsoleKit', '/org/freedesktop/ConsoleKit/Manager')
        manager = dbus.Interface (manager_obj, 'org.freedesktop.ConsoleKit.Manager')
    
        for sessionid in manager.GetSessions():
            session_obj = bus.get_object ('org.freedesktop.ConsoleKit', sessionid)
            session = dbus.Interface (session_obj, 'org.freedesktop.ConsoleKit.Session')
            if session.GetX11Display() == self.x11_display:
                
                self.unix_user=int(session.GetUnixUser())
                if self.unix_user > 900:
                    self.user=username(self.unix_user)
                
                self.since= str(session.GetCreationTime())
                self.active=True
                self.diff=self.diffnow(self.since)
                return

    def diffnow(self, date):
        diff=datetime.timedelta(0, time.mktime(time.gmtime()) - time.mktime(dateutil.parser.parse(date).timetuple()))
        """
        if days == 0:
                timelogged="%02dh:%02dm"%(hours,minutes)
            else:
                timelogged="%dd %02dh:%02dm"%(days,hours,minutes)
        """
        if diff.days > 0:
            return "%dd %s"%(diff.days, datetime.timedelta(0, diff.seconds))
        else:
            return "%s"%datetime.timedelta(0, diff.seconds)

class Sessions(object):
    def __init__(self):
        self.sessions=[]
        self.__get_all__()
        pass
    
    def __get_all__(self):
        bus = dbus.SystemBus ()
        manager_obj = bus.get_object ('org.gnome.DisplayManager', '/org/gnome/DisplayManager/Manager')
        manager = dbus.Interface (manager_obj, 'org.gnome.DisplayManager.Manager')

        sessions=[]
        for display in manager.GetDisplays():
            display_obj = bus.get_object ('org.gnome.DisplayManager', display)
            session = dbus.Interface (display_obj, 'org.gnome.DisplayManager.Display')
            self.sessions.append( Display(session) )

class Connections(object):
    def __init__(self):
        self.connections=[]
        self.__get_all__()
    
    def __get_all__(self):
        bus = dbus.SystemBus()
        manager_obj = bus.get_object ('org.freedesktop.ConsoleKit', '/org/freedesktop/ConsoleKit/Manager')
        manager = dbus.Interface (manager_obj, 'org.freedesktop.ConsoleKit.Manager')

        for sessionid in manager.GetSessions():
            session_obj = bus.get_object ('org.freedesktop.ConsoleKit', sessionid)
            session = dbus.Interface (session_obj, 'org.freedesktop.ConsoleKit.Session')
            
            userid=int(session.GetUnixUser())
            usernametxt=None
            active=False
            diff=None
            if str(session.GetSessionType()) != 'LoginWindow':#FIXME userid > 900: better???
                usernametxt=username(userid)
                active=True
                diff=self.diffnow(str(session.GetCreationTime()))
            
            con={'unix_user':userid,
                 'user':usernametxt,
                 'since':str(session.GetCreationTime()),
                 'active':active,
                 'diff':diff,
                 #'id':str(session.GetId()),
                 'is_local':bool(session.IsLocal()),
                 'remote_host_name':str(session.GetRemoteHostName()),
                 'x11_display':str(session.GetX11Display())
                }
            self.connections.append(con)

    def diffnow(self, date):
        diff=datetime.timedelta(0, time.mktime(time.gmtime()) - time.mktime(dateutil.parser.parse(date).timetuple()))
        """
        if days == 0:
                timelogged="%02dh:%02dm"%(hours,minutes)
            else:
                timelogged="%dd %02dh:%02dm"%(days,hours,minutes)
        """
        if diff.days > 0:
            return "%dd %s"%(diff.days, datetime.timedelta(0, diff.seconds))
        else:
            return "%s"%datetime.timedelta(0, diff.seconds)


class MultiSeat(Connections):
    def __init__(self):
        Connections.__init__(self)
        EMPTY={'is_local': None, 'unix_user': None, 'remote_host_name': None, 'active': None, 'diff': '', 'x11_display': '', 'since': '', 'user': ''}
        multiseats={}
        for seat in self.get_seats():
            multiseats[seat]=EMPTY
            multiseats[seat]['x11_display']=":%s"%seat
            isrunning=False
            for con in self.connections:
                if con['x11_display'] == ":%s"%seat:
                    multiseats[seat]=con
                    isrunning=True
            multiseats[seat]['running']=isrunning
        self.connections=multiseats

    def get_seats(self):
        if os.path.isdir('/dev/usbseat/'):
            return ['0'] + os.listdir('/dev/usbseat/')
        return ['0']


if __name__ == "__main__":
#    # search for last connection of user prueba
#    app=ConsoleKitHistory(None, last=False)
#    from pprint import pprint
#    for con in app.data:
#        pprint (con)
#        print "\n"


#    print "\n------------------------------\n"

#    # list all connections
#    app=Sessions()
#    for session in app.sessions:
#        print(session)
#        print "\n"

    app=Connections()
    for con in app.connections:
        print con
