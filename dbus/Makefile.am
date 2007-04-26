DBUS_CONF=/etc/dbus-1/system.d/
X11_CONF=/etc/X11/Xsession.d/
DESTDIR:=/
PREFIX:=/usr

all:
	

install:
	install -d  $(DESTDIR)$(DBUS_CONF)/
	install -d  $(DESTDIR)$(X11_CONF)/
	install -d  $(DESTDIR)/$(PREFIX)/bin/

	install -m 644 tcosmonitor.conf    $(DESTDIR)$(DBUS_CONF)/
	install -m 644 81tcos-dbus-client  $(DESTDIR)$(X11_CONF)/
	install -m 755 tcos-dbus-client.py $(DESTDIR)/$(PREFIX)/bin/tcos-dbus-client

clean:
	rm -f *.pyc *~
