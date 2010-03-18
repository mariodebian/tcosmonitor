#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 
# This script is inspired by the debian package python-chardet
import os
import glob
from distutils.core import setup
from distutils.command.build import build
from distutils.command.install_data import install_data as install_data


data_files = []

import sys

def get_debian_version():
    f=open('debian/changelog', 'r')
    line=f.readline()
    f.close()
    version=line.split()[1].replace('(','').replace(')','')
    return version

class build_locales(build):
    def run(self):
        #os.system("sh fix-glade.sh")
        os.system("cd po && make")

        # parse __VERSION__ in build_scripts
        for pyfile in glob.glob( "%s/*.py" %self.build_scripts):
            process_version(pyfile)
        
        libdir=self.build_lib + '/tcosmonitor'
        for pyfile in glob.glob( "%s/*.py" %libdir):
            process_version(pyfile)
            
        extdir=libdir+'/extensions'
        for pyfile in glob.glob( "%s/*.py" %extdir):
            process_version(pyfile)
        
        build.run(self)

class tcosmonitor_install_data(install_data):
    def run(self):
        install_data.run(self)
        
        # rename scripts (delete .py extension)
        for pyfile in glob.glob(self.install_dir + '/bin/*.py'):
            new=pyfile.split('.py')[0]
            print(" * Renaming %s => %s" %(pyfile, new ) )
            os.rename( pyfile, new )
        

def process_version(pyfile):
    version=get_debian_version()
    print("sed -i -e 's/__VERSION__/%s/g' %s" %(version, pyfile) )
    os.system("sed -i -e 's/__VERSION__/%s/g' %s" %(version, pyfile) )

for (path, dirs, files) in os.walk("po"):
    if "tcosmonitor.mo" in files:
        target = path.replace("po", "share/locale", 1)
        data_files.append((target, [os.path.join(path, "tcosmonitor.mo")]))

def get_files(ipath):
    files = []
    for afile in glob.glob('%s/*'%(ipath) ):
        if os.path.isfile(afile):
            files.append(afile)
    return files

# images (menus and buttons)
data_files.append(('share/tcosmonitor/images', get_files("images") ))
data_files.append(('share/pixmaps', ['images/tcos-icon-32x32.png'] ))

# Glade files
#data_files.append(('share/tcosmonitor', ['tcosmonitor.glade', 
#                                         'tcospersonalize.glade',
#                                         'tcos-volume-manager.glade',
#                                         'tray.glade'] ))
data_files.append(('share/tcosmonitor/ui', get_files("ui") ))


# config files and Xsession.d launcher
data_files.append( ('/etc/tcos', ['tcosmonitor.conf']) )
data_files.append( ('/etc/tcos', ['tcos-devices-ng.conf']) )
data_files.append( ('/etc/X11/Xsession.d', ['dbus/81tcos-utils']) )

# Desktop files
data_files.append( ('share/applications/', ['tcosmonitor.desktop', 
                                            'tcospersonalize.desktop',
                                            'tcos-volume-manager.desktop']) )


setup(name='TcosMonitor',
      description = 'Thin Client Manager for teachers',
      version=get_debian_version(),
      author = 'Mario Izquierdo',
      author_email = 'mariodebian@gmail.com',
      url = 'http://www.tcosproject.org',
      license = 'GPLv2',
      platforms = ['linux'],
      keywords = ['thin client', 'teacher monitor', 'ltsp'],
      packages=['tcosmonitor', 'tcosmonitor.extensions'],
      package_dir = {'':''},
      scripts=['tcosmonitor.py', 'tcos-volume-manager.py', 'tcos-devices-ng.py', 
                'tcospersonalize.py', 'dbus/tcos-dbus-client.py',
                'server-utils/tcos-server-utils.py'],
      cmdclass = {'build': build_locales, 'install_data' : tcosmonitor_install_data},
      data_files=data_files
      )

