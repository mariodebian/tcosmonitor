#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 
# This script is inspired by the debian package python-chardet
import os
import glob
from distutils.core import setup
from distutils.command.build import build

data_files = []

import sys

class build_locales(build):
    if not "clean" in sys.argv:
        #os.system("sh fix-glade.sh")
        os.system("cd po && make")

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
data_files.append(('share/tcosmonitor', ['tcosmonitor.glade'] ))
data_files.append(('share/tcosmonitor', ['tcospersonalize.glade'] ))
data_files.append(('share/tcosmonitor', ['tcos-volume-manager.glade'] ))
data_files.append(('share/tcosmonitor', ['tray.glade'] ))


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
      version='__VERSION__',
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
      cmdclass = {'build': build_locales},
      data_files=data_files
      )

