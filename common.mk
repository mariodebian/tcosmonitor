#.SILENT:

MAKE=make -B
INSTALL=install

VERSION=$(shell head -1 debian/changelog 2>/dev/null | awk  '{gsub(/\(/,"",$$2); gsub(/\)/, "" , $$2); print $$2}' )

have_changelog := $(wildcard debian/changelog)
ifeq ($(strip $(have_changelog)),)
VERSION=$(shell head -1 ../debian/changelog 2>/dev/null | awk  '{gsub(/\(/,"",$$2); gsub(/\)/, "" , $$2); print $$2}' )
endif



PACKAGE=tcosmonitor


TCOS_DIR=$(shell awk -F "=" '/TCOS_DIR=/ {print $$2}' /etc/tcos/tcos.conf )
TCOS_BINS=$(shell awk -F "=" '/TCOS_BINS=/ {print $$2}' /etc/tcos/tcos.conf )
TCOS_XMLRPC_DIR=$(PREFIX)/share/tcosmonitor/xmlrpc/
DBUS_CONF=/etc/dbus-1/system.d/
X11_CONF=/etc/X11/Xsession.d/

project=tcosmonitor


# debian or ubuntu ???
HAVE_DEBIAN=$(shell grep -i debian /etc/issue)
HAVE_UBUNTU=$(shell grep -i ubuntu /etc/issue)

ifeq ( $(strip $(HAVE_DEBIAN)),)
DEB_MIRROR=http://archive.ubuntu.com/ubuntu/
else
DEB_MIRROR=http://ftp.uk.debian.org/debian/
endif

#BUSYBOX_FILE=$(shell apt-cache show busybox-static|awk '/^Filename/ {print $$2}'| head -1)


PREFIX:=/usr


test:
	@echo "------------------------------------"
	@echo VERSION=$(VERSION)
	@echo PACKAGE=$(PACKAGE)
	@echo 
	@echo PREFIX=$(PREFIX)
	@echo DESTDIR=$(DESTDIR)
	@echo
	@echo CURDIR=$(CURDIR)
	@echo 
	@echo TCOS_DIR=$(TCOS_DIR)
	@echo TCOS_BINS=$(TCOS_BINS)
	@echo TCOS_XMLRPC_DIR=$(TCOS_XMLRPC_DIR)
	@echo DBUS_CONF=$(DBUS_CONF)
	@echo x11_CONF=$(X11_CONF)
	@echo
	@echo HAVE_DEBIAN=$(HAVE_DEBIAN)
	@echo HAVE_UBUNTU=$(HAVE_UBUNTU)
	@echo DEB_MIRROR=$(DEB_MIRROR)
	@echo "------------------------------------"
