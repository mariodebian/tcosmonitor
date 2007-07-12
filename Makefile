all: fix-glade es.gmo tcosxmlrpc dbus udev

include common.mk


printversion:
	echo $(VERSION)

test-all:
	@$(MAKE) test
	@cd xmlrpc &&  $(MAKE) test
	@cd udev &&    $(MAKE) test
#	@cd busybox && $(MAKE) test && $(MAKE) test2
	@cd dbus &&    $(MAKE) test

dist-clean:
	cd busybox && $(MAKE) dist-clean
	

clean:
	rm -f *~ *.pyc *.orig *.bak *-stamp
	cd xmlrpc && $(MAKE) clean
	cd lockscreen && $(MAKE) clean
	cd po && rm -rf es/
	$(MAKE) -f Makefile.ltsp clean
	cd dbus && $(MAKE) clean

tcosxmlrpc:
	cd xmlrpc && $(MAKE)
	cd lockscreen && $(MAKE)

busybox_static:
	if [ ! -f busybox/busybox ]; then cd busybox && $(MAKE) ; fi

glade:
	glade-2 $(PACKAGE).glade
	$(MAKE) fix-glade

fix-glade:
	bash fix-glade.sh

exec:
	python2.4 $(PACKAGE).py --debug

gedit:
	gedit *.py >/dev/null 2>&1 &

gedit-cvs:
	gedit-cvs *.py >/dev/null 2>&1 &


pot:
	xgettext  -o po/tcosmonitor.pot --files-from=po/FILES

es.po:
	rm -f po/$(PACKAGE).glade.pot
	msginit --input po/$(PACKAGE).pot -o po/es-new.po
	msgmerge -o po/es-new.po po/es.po po/$(PACKAGE).pot
	##################################################
	#           translate po/es-new.po               #
	##################################################

es.gmo:
	if [ -f po/es-new.po ]; then  mv po/es-new.po po/es.po ; fi
	mkdir -p po/es/LC_MESSAGES/
	msgfmt -o po/es/LC_MESSAGES/$(PACKAGE).mo po/es.po

dbus:
	cd dbus && $(MAKE)

udev:
	cd udev && $(MAKE)


install:
	#  Creating tcos-config directories in $(DESTDIR)/
	install -d $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/images
	install -d $(DESTDIR)/$(PREFIX)/share/applications/
	install -d $(DESTDIR)/$(PREFIX)/share/pixmaps/
	install -d $(DESTDIR)/$(PREFIX)/bin
	install -d $(DESTDIR)/$(PREFIX)/sbin
	install -d $(DESTDIR)/$(TCOS_BINS)
	install -d $(DESTDIR)/etc/tcos/
	

	# Installing tcosmonitor in  $(DESTDIR)
	install -m 644 $(PACKAGE).glade $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)
	install -m 644 tcospersonalize.glade $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)
	install -m 644 tcos-volume-manager.glade $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)
	install -m 644 tcos-devices.glade $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)

	# install all images
	for i in `ls images/*png`; do install -m 644 $$i $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/$$i; done

	install -m 644 tcosmonitor.desktop $(DESTDIR)/$(PREFIX)/share/applications/
	install -m 644 tcospersonalize.desktop $(DESTDIR)/$(PREFIX)/share/applications/
	install -m 644 images/tcos-icon-32x32.png $(DESTDIR)/$(PREFIX)/share/pixmaps/

	install -m 644 tcosmonitor.conf $(DESTDIR)/etc/tcos/

	install -m 644 Initialize.py  $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 shared.py      $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 LocalData.py   $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 TcosXmlRpc.py  $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 TcosConf.py    $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 TcosDBus.py    $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 TcosActions.py  $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 TcosXauth.py    $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 ping.py         $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 htmltextview.py     $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 TcosTrayIcon.py     $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/

	install -m 755 tcosmonitor.py           $(DESTDIR)/$(PREFIX)/bin/tcosmonitor
	install -m 755 tcospersonalize.py       $(DESTDIR)/$(PREFIX)/bin/tcospersonalize
	install -m 755 tcos-volume-manager.py   $(DESTDIR)/$(PREFIX)/bin/tcos-volume-manager
	install -m 755 tcos-devices.py          $(DESTDIR)/$(PREFIX)/bin/tcos-devices
	install -m 755 tcos-devices-ng.py       $(DESTDIR)/$(PREFIX)/bin/tcos-devices-ng

	install -m 755 server-utils/tcos-server-utils.py          $(DESTDIR)/$(PREFIX)/sbin/tcos-server-utils

#	install -m 644 tcos-devices-daemon.desktop      $(DESTDIR)/etc/xdg/autostart/
#	install -m 644 tcos-devices-autostart.desktop   $(DESTDIR)/etc/xdg/autostart/
#	install -m 644 tcos-devices.desktop             $(DESTDIR)$(PREFIX)/share/applications/
#	install -m 644 tcos-volume-manager.desktop      $(DESTDIR)$(PREFIX)/share/applications/
#	install -m 644 tcos-volume-manager.desktop      $(DESTDIR)/etc/xdg/autostart/

	# locales
	install -d $(DESTDIR)/$(PREFIX)/share/locale/es/LC_MESSAGES/
	install -m 644 po/es/LC_MESSAGES/$(PACKAGE).mo $(DESTDIR)/$(PREFIX)/share/locale/es/LC_MESSAGES/$(PACKAGE).mo
	
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
	install -d $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/xmlrpc/

	install -m 755 lockscreen/lockscreen $(DESTDIR)/$(TCOS_BINS)/lockscreen
	install -m 644 lockscreen/locked.png $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/xmlrpc/locked.png

	# install tcos hooks
	install -d $(DESTDIR)$(TCOS_DIR)/hooks-addons/
	install -m 644 hooks-addons/tcosmonitor $(DESTDIR)$(TCOS_DIR)/hooks-addons/


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
	sudo dpkg -i ../tcosmonitor_*deb  ../tcos-tcosmoni*deb


patch_version:
	# PATCHING VERSION
	sed -i 's/__VERSION__/$(VERSION)/g' shared.py
	sed -i 's/__VERSION__/$(VERSION)/g' Initialize.py
	sed -i 's/__VERSION__/$(VERSION)/g' LocalData.py
	sed -i 's/__VERSION__/$(VERSION)/g' ping.py
	sed -i 's/__VERSION__/$(VERSION)/g' TcosActions.py
	sed -i 's/__VERSION__/$(VERSION)/g' TcosConf.py
	sed -i 's/__VERSION__/$(VERSION)/g' TcosDBus.py
	sed -i 's/__VERSION__/$(VERSION)/g' TcosXauth.py
	sed -i 's/__VERSION__/$(VERSION)/g' TcosXmlRpc.py
	sed -i 's/__VERSION__/$(VERSION)/g' tcos-devices-ng.py
	sed -i 's/__VERSION__/$(VERSION)/g' tcos-devices.py
	sed -i 's/__VERSION__/$(VERSION)/g' tcos-volume-manager.py
	sed -i 's/__VERSION__/$(VERSION)/g' tcosmonitor.py
	sed -i 's/__VERSION__/$(VERSION)/g' server-utils/tcos-server-utils.py

patch_dapper: patch_version
	# PATCHING TcosMonitor in Ubuntu DAPPER
	sed -i '/^Build/s/5.0.37.2/5.0.7ubuntu13/g' debian/control
	sed -i '/python-support/s/0.3/0.1.1ubuntu1/g' debian/control
	sed -i '/dh_pysupport/s/dh_pysupport/dh_python/g' debian/rules

	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcos-devices.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcos-devices-ng.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcosmonitor.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcospersonalize.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcos-volume-manager.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' server-utils/tcos-server-utils.py

patch_edgy: patch_version
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcos-devices.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcos-devices-ng.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcosmonitor.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcospersonalize.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcos-volume-manager.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' server-utils/tcos-server-utils.py

patch_feisty: patch_version

patch_gutsy: patch_version

patch_etch: patch_version
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcos-devices.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcos-devices-ng.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcosmonitor.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcospersonalize.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcos-volume-manager.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' server-utils/tcos-server-utils.py

patch_unstable: patch_version


.PHONY: fix-glade es.gmo tcosxmlrpc dbus udev
