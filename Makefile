all: fix-glade busybox_static es.gmo tcosxmlrpc dbus udev

include common.mk


printversion:
	echo $(VERSION)

test-all:
	@$(MAKE) test
	@cd xmlrpc &&  $(MAKE) test
	@cd udev &&    $(MAKE) test
	@cd busybox && $(MAKE) test && $(MAKE) test2
	@cd dbus &&    $(MAKE) test

dist-clean:
	cd busybox && $(MAKE) dist-clean
	

clean:
	rm -f *~ *.pyc *.orig *.bak *-stamp
	if [ -d debian/tmp ]; then rm -rf debian/tmp; fi
	if [ -d debian/tcosmonitor ]; then rm -rf debian/tcosmonitor; fi
	if [ -d debian/pxes-1.0-tcosmonitor ]; then rm -rf debian/pxes-1.0-tcosmonitor; fi
	if [ -d debian/pxes-1.1-tcosmonitor ]; then rm -rf debian/pxes-1.1-tcosmonitor; fi
	if [ -d debian/pxes-1.2-tcosmonitor ]; then rm -rf debian/pxes-1.2-tcosmonitor; fi
	if [ -d debian/ltsp-tcosmonitor ]; then rm -rf debian/ltsp-tcosmonitor; fi
	if [ -d debian/tcos-tcosmonitor ]; then rm -rf debian/tcos-tcosmonitor; fi
	cd xmlrpc && $(MAKE) clean
	cd lockscreen && $(MAKE) clean
	cd po && rm -rf es/
	#rm -f debian/*substvars debian/*debhelper
	$(MAKE) -f Makefile.ltsp clean
	cd dbus && $(MAKE) clean

validate-xml:
	cd httpd && sh webserver.sh 2>/dev/null && xmlstarlet val system-info.xml
	rm -f httpd/system-info.xml

tcosxmlrpc:
	cd xmlrpc && $(MAKE)
	cd lockscreen && $(MAKE)

busybox_static:
	if [ ! -f busybox/busybox ]; then cd busybox && $(MAKE) ; fi

glade:
	glade-2 $(project).glade
	$(MAKE) fix-glade

fix-glade:
	sh fix-glade.sh

exec:
	python2.4 $(project).py --debug

gedit:
	gedit *.py >/dev/null 2>&1 &

gedit-cvs:
	gedit-cvs *.py >/dev/null 2>&1 &


pot:
	xgettext  -o po/tcosmonitor.pot --files-from=po/FILES

es.po:
	rm -f po/$(project).glade.pot
	msginit --input po/$(project).pot -o po/es-new.po
	msgmerge -o po/es-new.po po/es.po po/$(project).pot
	##################################################
	#           translate po/es-new.po               #
	##################################################

es.gmo:
	if [ -f po/es-new.po ]; then  mv po/es-new.po po/es.po ; fi
	mkdir -p po/es/LC_MESSAGES/
	msgfmt -o po/es/LC_MESSAGES/$(project).mo po/es.po

dbus:
	cd dbus && $(MAKE)

udev:
	cd udev && $(MAKE)


install:
	#  Creating tcos-config directories in $(DESTDIR)/
	install -d $(DESTDIR)/$(PREFIX)/share/$(project)/images
	install -d $(DESTDIR)/$(PREFIX)/share/applications/
	install -d $(DESTDIR)/$(PREFIX)/share/pixmaps/
	install -d $(DESTDIR)/$(PREFIX)/bin
	install -d $(DESTDIR)/$(PREFIX)/sbin
	install -d $(DESTDIR)/$(TCOS_BINS)
	install -d $(DESTDIR)/etc/xdg/autostart/
	

	# Installing tcosmonitor in  $(DESTDIR)
	install -m 644 $(project).glade $(DESTDIR)/$(PREFIX)/share/$(project)
	install -m 644 tcospersonalize.glade $(DESTDIR)/$(PREFIX)/share/$(project)
	install -m 644 tcos-volume-manager.glade $(DESTDIR)/$(PREFIX)/share/$(project)
	install -m 644 tcos-devices.glade $(DESTDIR)/$(PREFIX)/share/$(project)

	# install all images
	for i in `ls images/*png`; do install -m 644 $$i $(DESTDIR)/$(PREFIX)/share/$(project)/$$i; done

	install -m 644 tcosmonitor.desktop $(DESTDIR)/$(PREFIX)/share/applications/
	install -m 644 tcospersonalize.desktop $(DESTDIR)/$(PREFIX)/share/applications/
	install -m 644 images/tcos-icon-32x32.png $(DESTDIR)/$(PREFIX)/share/pixmaps/

	install -m 644 Initialize.py  $(DESTDIR)/$(PREFIX)/share/$(project)/
	install -m 644 shared.py      $(DESTDIR)/$(PREFIX)/share/$(project)/
	install -m 644 LocalData.py   $(DESTDIR)/$(PREFIX)/share/$(project)/
	install -m 644 TcosXmlRpc.py  $(DESTDIR)/$(PREFIX)/share/$(project)/
	install -m 644 TcosConf.py    $(DESTDIR)/$(PREFIX)/share/$(project)/
	install -m 644 TcosDBus.py    $(DESTDIR)/$(PREFIX)/share/$(project)/
	install -m 644 TcosActions.py    $(DESTDIR)/$(PREFIX)/share/$(project)/
	install -m 644 TcosXauth.py    $(DESTDIR)/$(PREFIX)/share/$(project)/
	install -m 644 ping.py        $(DESTDIR)/$(PREFIX)/share/$(project)/
	install -m 644 htmltextview.py        $(DESTDIR)/$(PREFIX)/share/$(project)/

	install -m 755 tcosmonitor.py           $(DESTDIR)/$(PREFIX)/bin/tcosmonitor
	install -m 755 tcospersonalize.py       $(DESTDIR)/$(PREFIX)/bin/tcospersonalize
	install -m 755 tcos-volume-manager.py   $(DESTDIR)/$(PREFIX)/bin/tcos-volume-manager
	install -m 755 tcos-devices.py          $(DESTDIR)/$(PREFIX)/bin/tcos-devices

	install -m 755 server-utils/tcos-server-utils.py          $(DESTDIR)/$(PREFIX)/sbin/tcos-server-utils

	install -m 644 tcos-devices-daemon.desktop      $(DESTDIR)/etc/xdg/autostart/
	install -m 644 tcos-devices-autostart.desktop   $(DESTDIR)/etc/xdg/autostart/
	install -m 644 tcos-devices.desktop             $(DESTDIR)$(PREFIX)/share/applications/

	# locales
	install -d $(DESTDIR)/$(PREFIX)/share/locale/es/LC_MESSAGES/
	install -m 644 po/es/LC_MESSAGES/$(project).mo $(DESTDIR)/$(PREFIX)/share/locale/es/LC_MESSAGES/$(project).mo
	
	# xmlrpc
	cd xmlrpc && $(MAKE) install PREFIX=$(PREFIX) DESTDIR=$(DESTDIR)

	# dbus
	cd dbus && $(MAKE) install PREFIX=$(PREFIX) DESTDIR=$(DESTDIR)

	# udev
	cd udev && $(MAKE) install PREFIX=$(PREFIX) DESTDIR=$(DESTDIR) TCOS_BINS=$(TCOS_BINS)


install-pxes1.0:
	@echo "Making pxes-1.0"
	@$(MAKE) -f Makefile.pxes PXES_VERSION=1.0 install

install-pxes1.1:
	@echo "Making pxes-1.1"
	@$(MAKE) -f Makefile.pxes PXES_VERSION=1.1 install
	
install-pxes1.2:
	@echo "Making pxes-1.2"
	@$(MAKE) -f Makefile.pxes PXES_VERSION=1.2 install

install-ltsp:
	@echo "Making ltsp"
	@$(MAKE) -f Makefile.ltsp install

install-tcos:
	install -d $(DESTDIR)/etc/tcos
	install -d $(DESTDIR)/$(PREFIX)/sbin
	install -d $(DESTDIR)/$(PREFIX)/bin
	install -d $(DESTDIR)/$(TCOS_DIR)/bin
	install -d $(DESTDIR)/$(PREFIX)/share/$(project)/xmlrpc/

	# some bins
#	install -m 755 xmlrpc/tcosxmlrpc $(DESTDIR)/$(TCOS_DIR)/bin/tcosxmlrpc
#	install -m 755 lockscreen/lockscreen $(DESTDIR)/$(TCOS_DIR)/bin/lockscreen
#	install -m 755 xmlrpc/hex2ascii $(DESTDIR)/$(TCOS_DIR)/bin/hex2ascii

#	install -m 755 xmlrpc/tcosxmlrpc     $(DESTDIR)/$(TCOS_BINS)/tcosxmlrpc
	install -m 755 lockscreen/lockscreen $(DESTDIR)/$(TCOS_BINS)/lockscreen
#	install -m 755 xmlrpc/hex2ascii      $(DESTDIR)/$(TCOS_BINS)/hex2ascii

#	install -m 755 xmlrpc/tcospasswd $(DESTDIR)/$(PREFIX)/sbin/tcospasswd
#	install -m 755 xmlrpc/sh/update-tcospasswd.sh $(DESTDIR)/$(PREFIX)/sbin/update-tcospasswd

	# install tcos hooks
	install -d $(DESTDIR)$(TCOS_DIR)/hooks-addons/
	install -m 644 hooks-addons/tcosmonitor $(DESTDIR)$(TCOS_DIR)/hooks-addons/

#	# Install tcosxmlrpc utils
#	install -m 755 xmlrpc/sh/screenshot.sh $(DESTDIR)/$(PREFIX)/share/$(project)/xmlrpc/
#	install -m 755 xmlrpc/sh/soundctl.sh   $(DESTDIR)/$(PREFIX)/share/$(project)/xmlrpc/
#	install -m 755 xmlrpc/sh/starthttpd.sh $(DESTDIR)/$(PREFIX)/share/$(project)/xmlrpc/starthttpd
#	install -m 755 xmlrpc/sh/getinfo.sh    $(DESTDIR)/$(PREFIX)/share/$(project)/xmlrpc/getinfo.sh
#	install -m 755 xmlrpc/sh/useallmodules.sh $(DESTDIR)/$(PREFIX)/share/$(project)/xmlrpc/useallmodules.sh
#	install -m 755 xmlrpc/sh/devicesctl.sh $(DESTDIR)/$(PREFIX)/share/$(project)/xmlrpc/devicesctl.sh

	# Install tcosxmlrpc utils
#	install -m 755 xmlrpc/sh/screenshot.sh $(DESTDIR)/$(TCOS_BINS)/
#	install -m 755 xmlrpc/sh/soundctl.sh   $(DESTDIR)/$(TCOS_BINS)/
#	install -m 755 xmlrpc/sh/starthttpd.sh $(DESTDIR)/$(TCOS_BINS)/
#	install -m 755 xmlrpc/sh/getinfo.sh    $(DESTDIR)/$(TCOS_BINS)/
#	install -m 755 xmlrpc/sh/useallmodules.sh $(DESTDIR)/$(TCOS_BINS)/
#	install -m 755 xmlrpc/sh/devicesctl.sh $(DESTDIR)/$(TCOS_BINS)/

#	install -m 755 xmlrpc/var/etc/httpd2.conf $(DESTDIR)/$(PREFIX)/share/$(project)/xmlrpc/
#	install -m 644 xmlrpc/var/etc/abyss.conf $(DESTDIR)/$(PREFIX)/share/$(project)/xmlrpc/
#	install -m 644 xmlrpc/var/etc/mime.types $(DESTDIR)/$(PREFIX)/share/$(project)/xmlrpc/


targz: clean
	rm -rf ../tmp 2> /dev/null
	mkdir ../tmp
	cp -ra * ../tmp
	rm -rf `find ../tmp/* -type d -name .svn`
	mv ../tmp ../tcosmonitor-$(VERSION)
	tar -czf ../tcosmonitor-$(VERSION).tar.gz ../tcosmonitor-$(VERSION)
	rm -rf ../tcosmonitor-$(VERSION)

tcos:
	rm -f ../tcosmonitor_*deb ../pxes-*-tcosmonitor*deb ../ltsp-tcos*deb ../tcos-tcosmon*deb
	dpkg-buildpackage -us -uc -rfakeroot
	#debuild -uc -us; true
	sudo dpkg -i ../tcosmonitor_*deb ../pxes-1.2-tcosmonitor*deb ../ltsp-tcos*deb ../tcos-tcosmoni*deb

.PHONY: fix-glade busybox_static es.gmo tcosxmlrpc dbus udev
