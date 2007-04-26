# $Id: Makefile.am 75 2006-10-18 22:40:32 mariodebian $
#
# This file is part of TcosMonitor.
#
# TcosMonitor is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# TcosMonitor is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TcosMonitor; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA.

EXTRA_DIST = bootstrap.sh README LICENSE
SUBDIRS=dbus hooks-addons lockscreen server-utils udev xmlrpc

#MAINTAINERCLEANFILES=README
#noinst_DATA = README


VERSION=$(shell head -1 debian/changelog | awk  '{gsub(/\(/,"",$$2); gsub(/\)/, "" , $$2); print $$2}' )
PACKAGE=tcosmonitor


TCOS_DIR=$(shell awk -F "=" '/TCOS_DIR=/ {print $$2}' /etc/tcos/tcos.conf )
TCOS_BINS=$(shell awk -F "=" '/TCOS_BINS=/ {print $$2}' /etc/tcos/tcos.conf )

project=tcosmonitor


#all: fix-glade busybox_static es.gmo tcosxmlrpc dbus udev

printversion:
	echo $(VERSION)

test:
	@echo TCOS_DIR=$(TCOS_DIR)
	@echo TCOS_BINS=$(TCOS_BINS)

pot:
	xgettext  -o po/tcosmonitor.pot --files-from=po/FILES

es.po:
	rm -f po/$(project).glade.pot
	msginit --input po/$(project).pot -o po/es-new.po
	msgmerge -o po/es-new.po po/es.po po/$(project).pot
	@echo "##################################################"
	@echo "#           translate po/es-new.po               #"
	@echo "##################################################"

es.gmo:
	if [ -f po/es-new.po ]; then  mv po/es-new.po po/es.po ; fi
	mkdir -p po/es/LC_MESSAGES/
	msgfmt -o po/es/LC_MESSAGES/$(project).mo po/es.po

.PHONY: es.gmo
