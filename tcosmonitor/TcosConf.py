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

import os
import sys
from time import time
import tcosmonitor.shared

def print_debug(txt):
    if tcosmonitor.shared.debug:
        print >> sys.stderr, "%s::%s" % (__name__, txt)
        #print("%s::%s" % (__name__, txt), file=sys.stderr)

def crono(start, txt):
    print_debug ("crono(), %s get %f seconds" %(txt, (time() - float(start))) )
    return

class TcosConf:
    def __init__(self, main, openfile=True):
        print_debug ( "__init__()" )
        self.main=main
        self.FirstRunning=False
        self.allnetworkinterfaces=[]
        #self.GetAllNetworkInterfaces()
        
        # reset memory data
        self.data=""
        self.vars=None
        self.use_secrets=False
        self.vars=[]
        self.vars_secrets=[]
        
        if openfile:
            self.CheckConfFile()
            self.reset()
        else:
            print_debug ( "__init__() not opening conf file" )
        
        
    def reset(self):
        print_debug("reset() reset data...")
        # reset memory data
        self.data=""
        self.vars=None
        self.vars=[]
        self.use_secrets=False
        self.vars_secrets=[]
        self.OpenFile()
    
    def OpenFile(self):
        self.CheckConfFile()
        conf=None
        conf=[]
        print_debug("open_file() reading data from \"%s\"..." \
                            %(tcosmonitor.shared.config_file) )
        try:
            fd=file(tcosmonitor.shared.config_file, 'r')
        except Exception, err:
            print("Error Opening %s file, error=%s"%(tcosmonitor.shared.config_file, err) )
            return
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
                (var, value)=conf[i].split("=", 1)
                self.vars.append([var, value])
                
        if os.path.isfile(tcosmonitor.shared.config_file_secrets):
            if self.main.ingroup_tcos == False and os.getuid() != 0:
                return
            try:
                fd=file(tcosmonitor.shared.config_file_secrets, 'r')
            except Exception, err:
                print("Error saving %s file, error=%s"%(tcosmonitor.shared.config_file_secrets, err) )
                return
            self.data=fd.readline()
            fd.close()
            if self.data != "\n":
                (var1, var2)=self.data.replace("\n", "").split(":")
                self.vars_secrets.append([var1, var2])
                self.use_secrets=True
        return
    
    def CheckConfFile(self):
        conf=None
        conf=[]
        if not os.path.isfile(tcosmonitor.shared.config_file):
            print_debug ( "CheckConfFile() %s not exists" %(tcosmonitor.shared.config_file) )
            self.CreateConfFile()
            return
        
        try:
            fd=file(tcosmonitor.shared.config_file, 'r')
        except Exception, err:
            print("Error Opening %s file, error=%s"%(tcosmonitor.shared.config_file, err) )
            return
        self.data=fd.readlines()
        fd.close()
        for line in self.data:
            if line != '\n':
                line=line.replace('\n', '')
                conf.append(line)
        if len(conf) <1:
            print_debug ( "CheckConfFile() FILE IS EMPTY!!!" )
            self.CreateConfFile()
            return
        
    def CreateConfFile(self):
        print_debug ( "CreateConfFile()" )
        # save this into file
        fd=file(tcosmonitor.shared.config_file, 'w')
        for item in tcosmonitor.shared.DefaultConfig:
            key=item[0]
            value=item[1]
            print_debug ("key=%s value=%s" %(key, value))
            fd.write("%s=%s\n" %(key, value) )
        fd.close()
        # make chmod 600
        os.chmod(tcosmonitor.shared.config_file, 0600)
        self.FirstRunning=True
        
    def SetVar(self, varname, value):
        print_debug ( "SetVar(%s)=\"%s\"" %(varname, value) )
        self.newdata=None
        self.newdata=[]
        for i in range(len(self.vars)):
            if varname == self.vars[i][0]:
                print_debug ( "changing value %s to %s of %s" \
                                %(self.vars[i][1], value, varname) )
                self.vars[i][1]="%s" %(value)
                return
        print_debug ("SetVar() WARNING var=%s value=%s not in vars!!!" %(varname, value))
            

    def SaveToFile(self):
        print_debug ( "SaveToFile() len(self.vars)=%d" %( len(self.vars) ) )
        if len(self.vars) < 1:
            print_debug ( "SaveToFile() self.vars is empty" )
            return
        
        fd=file(tcosmonitor.shared.config_file, 'w')
        for i in range(len(self.vars)):
            fd.write("%s=%s\n" %(self.vars[i][0], self.vars[i][1]))
        fd.close
        os.chmod(tcosmonitor.shared.config_file, 0600)
        print_debug ( "SaveToFile() new settings SAVED!!!")   
        return
    
    def GetVar(self, varname):
        if self.use_secrets:
            if varname == "xmlrpc_username":
                return self.vars_secrets[0][0]
            elif varname == "xmlrpc_password":
                return self.vars_secrets[0][1]
        for i in range( len(self.vars) ):
            if self.vars[i][0].find(varname) == 0:
                if self.vars[i][1] == "1":
                    return 1
                return self.vars[i][1]
        # search for new var
        for _var in tcosmonitor.shared.DefaultConfig:
            if _var[0] == varname:
                print_debug ( "GetVar() NEW VAR FOUND, %s, adding to list \"\""\
                                                 %(varname) )
                self.vars.append( [_var[0], _var[1], "new"] )
                return _var[1]
        print_debug ( "GetVar() not found, %s, returning \"\"" %(varname) )
        return ""
    
    def IsNew(self, varname):
        for var in self.vars:
            #print_debug("IsNew() searching in var %s" %var)
            if var[0] == varname and len(var) == 3 and var[2] == "new":
                return True
        print_debug("IsNew() self.vars=%s"%self.vars)
        print_debug("IsNew() var %s not found in self.vars"%varname)
        return False
    
        
if __name__ == '__main__':
    conf = TcosConf(None)
    
    conf.SetVar("xmlrpc_username", "user2")
    print_debug ( conf.vars )
    conf.SaveToFile()
    
