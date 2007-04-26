
PREFIX:=/usr
TCOS_XMLRPC_DIR=$(PREFIX)/share/tcosmonitor/xmlrpc/
TCOS_BINS:=/usr/lib/tcos
all:
	

install:
	install -d  $(DESTDIR)$(TCOS_XMLRPC_DIR)

	install -m 755 tcos-udevd.sh          $(DESTDIR)$(TCOS_BINS)/
	install -m 644 050_tcos_devices.rules $(DESTDIR)$(TCOS_XMLRPC_DIR)/

clean:
	rm -f *.pyc *~
