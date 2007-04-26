all:
	#none

include ../common.mk


install:
	install -d  $(DESTDIR)$(TCOS_XMLRPC_DIR)

	install -m 755 tcos-udevd.sh          $(DESTDIR)$(TCOS_BINS)/
	install -m 644 050_tcos_devices.rules $(DESTDIR)$(TCOS_XMLRPC_DIR)/

clean:
	rm -f *.pyc *~
