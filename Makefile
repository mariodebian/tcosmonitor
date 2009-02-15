all: fix-glade dbus

include common.mk


printversion:
	echo $(VERSION)

test-all:
	@$(MAKE) test
	@cd xmlrpc &&  $(MAKE) test
#	@cd busybox && $(MAKE) test && $(MAKE) test2
	@cd dbus &&    $(MAKE) test

dist-clean:
	cd busybox && $(MAKE) dist-clean
	

clean:
	rm -rf tmp build
	rm -f *~ *.pyc *.orig *.bak *-stamp *.glade.backup *gladep
	python setup.py clean
	cd tcosmonitor && rm -f *~ *.pyc *.orig *.bak *-stamp *.glade.backup
	find -name "*~" | xargs rm -f
	cd po && make clean
	cd dbus && $(MAKE) clean
	cd tcosmonitor/extensions && $(MAKE) clean


glade:
	glade-2 $(PACKAGE).glade
	$(MAKE) fix-glade

fix-glade:
	bash fix-glade.sh

exec:
	python $(PACKAGE).py --debug

pot:
	cd po && make pot

es.po:
	############################################################
	#   OBSOLETE Makefile target => cd po and make into it     #
	############################################################
	@exit 1

dbus:
	cd dbus && $(MAKE)


install:
	#  Creating tcos-config directories in $(DESTDIR)/
	install -d $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/images
	install -d $(DESTDIR)/$(PREFIX)/share/applications/
	install -d $(DESTDIR)/$(PREFIX)/share/pixmaps/
	install -d $(DESTDIR)/$(PREFIX)/bin
	install -d $(DESTDIR)/$(PREFIX)/sbin
	install -d $(DESTDIR)/etc/tcos/
	

	# Installing tcosmonitor in  $(DESTDIR)
	install -m 644 $(PACKAGE).glade $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)
	install -m 644 tcospersonalize.glade $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)
	install -m 644 tcos-volume-manager.glade $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)

	# install all images
	for i in `ls images/*png`; do install -m 644 $$i $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/$$i; done

	install -m 644 tcosmonitor.desktop $(DESTDIR)/$(PREFIX)/share/applications/
	install -m 644 tcospersonalize.desktop $(DESTDIR)/$(PREFIX)/share/applications/
	install -m 644 images/tcos-icon-32x32.png $(DESTDIR)/$(PREFIX)/share/pixmaps/

	install -m 644 tcosmonitor.conf     $(DESTDIR)/etc/tcos/
	install -m 644 tcos-devices-ng.conf $(DESTDIR)/etc/tcos/

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
	install -m 644 TcosTrayIcon2.py    $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 TcosStaticHosts.py  $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 TcosPreferences.py  $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 TcosCommon.py       $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 WakeOnLan.py        $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 TcosIconView.py     $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 TcosClassView.py    $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 TcosListView.py     $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 TcosMenus.py        $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/
	install -m 644 TcosExtensions.py   $(DESTDIR)/$(PREFIX)/share/$(PACKAGE)/

	install -m 755 tcosmonitor.py           $(DESTDIR)/$(PREFIX)/bin/tcosmonitor
	install -m 755 tcospersonalize.py       $(DESTDIR)/$(PREFIX)/bin/tcospersonalize
	install -m 755 tcos-volume-manager.py   $(DESTDIR)/$(PREFIX)/bin/tcos-volume-manager
	install -m 755 tcos-devices-ng.py       $(DESTDIR)/$(PREFIX)/bin/tcos-devices-ng


	install -m 755 server-utils/tcos-server-utils.py          $(DESTDIR)/$(PREFIX)/sbin/tcos-server-utils

	# locales
	cd po && make install DESTDIR=$(DESTDIR)
	
	# dbus
	cd dbus && $(MAKE) install PREFIX=$(PREFIX) DESTDIR=$(DESTDIR)

	# extensions
	cd extensions && $(MAKE) install PREFIX=$(PREFIX) DESTDIR=$(DESTDIR)

targz: clean
	rm -rf ../tmp 2> /dev/null
	mkdir ../tmp
	cp -ra * ../tmp
	rm -rf `find ../tmp/* -type d -name .svn`
	mv ../tmp ../tcosmonitor-$(VERSION)
	tar -czf ../tcosmonitor-$(VERSION).tar.gz ../tcosmonitor-$(VERSION)
	rm -rf ../tcosmonitor-$(VERSION)

patch_version:
	@for f in $(shell find -type f -name "*.py"); do \
		echo "  * Patching VERSION $(VERSION) in $$f"; \
		sed -i 's/__VERSION__/$(VERSION)/g' $$f; \
	done

patch_dapper: patch_version
	# PATCHING TcosMonitor in Ubuntu DAPPER
	sed -i '/^Build/s/5.0.37.2/5.0.7ubuntu13/g' debian/control
	sed -i '/python-support/s/0.3/0.1.1ubuntu1/g' debian/control
	sed -i '/dh_pysupport/s/dh_pysupport/dh_python/g' debian/rules

	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcos-devices-ng.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcosmonitor.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcospersonalize.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcos-volume-manager.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' server-utils/tcos-server-utils.py

patch_edgy: patch_version
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcos-devices-ng.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcosmonitor.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcospersonalize.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcos-volume-manager.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' server-utils/tcos-server-utils.py

patch_feisty: patch_version

patch_gutsy: patch_version

patch_max: patch_version

patch_etch: patch_version
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcos-devices-ng.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcosmonitor.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcospersonalize.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' tcos-volume-manager.py
	sed -i '/\/usr\/bin\/env/s/python/python2.4/g' server-utils/tcos-server-utils.py

patch_unstable: patch_version

patch_lenny: patch_version

patch_testing: patch_version

patch_hardy: patch_version

patch_max: patch_version
	sed -i '/show_donate/s/1/0/g' tcosmonitor/shared.py
	
patch_intrepid: patch_version

patch_jaunty: patch_version

.PHONY: fix-glade tcosxmlrpc dbus udev
