all:
	gcc -o mount_listener mount_listener.c

include ../common.mk


install:
	install -d  $(DESTDIR)$(TCOS_XMLRPC_DIR)
	install -d  $(DESTDIR)$(TCOS_BINS)

	install -m 755 tcos-udevd.sh          $(DESTDIR)$(TCOS_BINS)/
	install -m 755 mount_listener         $(DESTDIR)$(TCOS_BINS)/
	install -m 755 listener-daemon.sh     $(DESTDIR)$(TCOS_BINS)/
	install -m 644 050_tcos_devices.rules $(DESTDIR)$(TCOS_XMLRPC_DIR)/

clean:
	rm -f *.pyc *~ mount_listener
