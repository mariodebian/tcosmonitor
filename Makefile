all: dbus

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
	rm -f *~ *.pyc *.orig *.bak *-stamp
	python setup.py clean
	cd tcosmonitor && rm -f *~ *.pyc *.orig *.bak *-stamp
	find -name "*~" | xargs rm -f
	cd po && make clean
	cd dbus && $(MAKE) clean
	cd tcosmonitor/extensions && $(MAKE) clean


exec:
	python $(PACKAGE).py --debug

pot:
	cd po && make pot

gmo:
	cd po && make gmo

es.po:
	############################################################
	#   OBSOLETE Makefile target => cd po and make into it     #
	############################################################
	@exit 1

dbus:
	cd dbus && $(MAKE)


install:
	@echo use python setup.py --install

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


patch_unstable:
	# none

patch_lenny:
	# none

patch_testing:
	# none


patch_hardy:
	echo 6 > debian/compat
	sed -i 's/7\.0\.0/6\.0\.0/g' debian/control
	sed -i 's/3\.8\.0/3\.7\.2/g' debian/control

patch_max:
	sed -i '/show_donate/s/1/0/g' tcosmonitor/shared.py
	sed -i '/show_about/s/1/0/g' tcosmonitor/shared.py
	
patch_intrepid:
	# none

patch_jaunty:
	# none

patch_karmic:
	# none




.PHONY: dbus
