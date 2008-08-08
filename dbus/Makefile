DESTDIR:=/

all:
	

include ../common.mk

install:
	install -d  $(DESTDIR)$(X11_CONF)/
	install -d  $(DESTDIR)/$(PREFIX)/bin/

	install -m 644 81tcos-utils  $(DESTDIR)$(X11_CONF)/
	install -m 755 tcos-dbus-client.py $(DESTDIR)/$(PREFIX)/bin/tcos-dbus-client

clean:
	rm -f *.pyc *~
