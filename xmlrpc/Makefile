all: server tcospasswd hex2ascii


include ../common.mk


CFLAGS=-Wall -ansi -pedantic `xmlrpc-c-config abyss-server --cflags`
LIBS=`xmlrpc-c-config abyss-server --libs` -lcrypt -lX11
DEFINES= -DBSIZE=512 -DVERSION=\"$(VERSION)\"
TEST_DEFINES=-DDEBUG -DVERSION=\"$(VERSION)\" -DBSIZE=512 -DVISIBLE_PASSWD
GCC=gcc
SERVER=tcosxmlrpc






server:
	$(GCC) $(DEFINES) -o $(SERVER) $(CFLAGS) $(LIBS) $(SERVER).c

debug:
	$(GCC) $(TEST_DEFINES) -o $(SERVER) $(CFLAGS) $(LIBS) $(SERVER).c

hex2ascii:
	$(GCC) hex2ascii.c -o hex2ascii -Wall -ansi -pedantic


validate-tcos:
	$(GCC) $(DEFINES) -o validate-tcos $(CFLAGS) $(LIBS) validate-tcos.c

tcospasswd:
	$(GCC) $(DEFINES) -o tcospasswd tcospasswd.c -lcrypt

#tcosmd5:
#	cd md5 && make md5c.o
#	$(GCC) -o tcosmd5 tcosmd5.c $(MD5)

clean:
#	cd md5 && make clean
	rm -f $(SERVER) tcosmd5 prueba prueba2 prueba3 validate-tcos tcospasswd var/log.txt var/log/* *~ hex2ascii

run:
	./$(SERVER) var/etc/abyss.conf

#debug:
#	XMLRPC_TRACE_XML=1 XMLRPC_TRACE_ABYSS=1 ABYSS_TRACE_CONN=1 ABYSS_TRACE_SOCKET=1 ./$(SERVER) var/etc/abyss.conf

client:
	python2.4 test/client.py

kill:
	killall $(SERVER) ; true


install:
	install -d $(DESTDIR)/$(TCOS_BINS)
	install -d $(DESTDIR)/$(PREFIX)/share/tcosmonitor/xmlrpc/
	install -d $(DESTDIR)/$(PREFIX)/sbin
    
	install -m 755 tcosxmlrpc     $(DESTDIR)/$(TCOS_BINS)/tcosxmlrpc
	install -m 755 hex2ascii      $(DESTDIR)/$(TCOS_BINS)/hex2ascii

	install -m 755 tcospasswd $(DESTDIR)/$(PREFIX)/sbin/tcospasswd
	install -m 755 sh/update-tcospasswd.sh $(DESTDIR)/$(PREFIX)/sbin/update-tcospasswd
	
	# Install tcosxmlrpc utils
	install -m 755 sh/screenshot.sh $(DESTDIR)/$(TCOS_BINS)/
	install -m 755 sh/soundctl.sh   $(DESTDIR)/$(TCOS_BINS)/
	install -m 755 sh/starthttpd.sh $(DESTDIR)/$(TCOS_BINS)/
	install -m 755 sh/getinfo.sh    $(DESTDIR)/$(TCOS_BINS)/
	install -m 755 sh/useallmodules.sh $(DESTDIR)/$(TCOS_BINS)/
	install -m 755 sh/devicesctl.sh $(DESTDIR)/$(TCOS_BINS)/

	install -m 755 var/etc/httpd2.conf $(DESTDIR)/$(PREFIX)/share/tcosmonitor/xmlrpc/
	install -m 644 var/etc/abyss.conf $(DESTDIR)/$(PREFIX)/share/tcosmonitor/xmlrpc/
	install -m 644 var/etc/mime.types $(DESTDIR)/$(PREFIX)/share/tcosmonitor/xmlrpc/
