all: server standalone tcospasswd


include ../common.mk


CFLAGS=-Wall -ansi -pedantic `xmlrpc-c-config abyss-server --cflags`
LIBS=`xmlrpc-c-config abyss-server --libs` -lcrypt -lX11
DEFINES= -DBSIZE=512 -DVERSION=\"$(VERSION)\"
TEST_DEFINES=-DDEBUG -DVERSION=\"$(VERSION)\" -DBSIZE=512 -DVISIBLE_PASSWD
GCC=gcc
SERVER=tcosxmlrpc

STANDALONE=tcosxmlrpc-standalone



server:
	$(GCC) $(DEFINES) -o $(SERVER) $(CFLAGS) $(LIBS) $(SERVER).c -DTCOS_PATH=\"/sbin\"

standalone:
	$(GCC) $(DEFINES) -o $(STANDALONE) $(CFLAGS) $(LIBS) $(SERVER).c -DTCOS_PATH=\"$(TCOS_BINS)\"

debug:
	$(GCC) $(TEST_DEFINES) -o $(SERVER) $(CFLAGS) $(LIBS) $(SERVER).c


validate-tcos:
	$(GCC) $(DEFINES) -o validate-tcos $(CFLAGS) $(LIBS) validate-tcos.c

tcospasswd:
	$(GCC) $(DEFINES) -o tcospasswd tcospasswd.c -lcrypt


clean:
#	cd md5 && make clean
	rm -f $(SERVER) $(STANDALONE) tcosmd5 prueba prueba2 prueba3 validate-tcos tcospasswd var/log.txt var/log/* *~

run:
	./$(SERVER) var/etc/abyss.conf


client:
	python2.4 test/client.py

kill:
	killall $(SERVER) ; true


install:
	install -d $(DESTDIR)/$(TCOS_BINS)
	install -d $(DESTDIR)/$(PREFIX)/share/tcosmonitor/xmlrpc/
	install -d $(DESTDIR)/$(PREFIX)/sbin
    
	install -m 755 $(SERVER)       $(DESTDIR)/$(TCOS_BINS)/
	install -m 755 $(STANDALONE)   $(DESTDIR)/$(TCOS_BINS)/

	install -m 755 tcospasswd $(DESTDIR)/$(PREFIX)/sbin/tcospasswd
	install -m 755 sh/update-tcospasswd.sh $(DESTDIR)/$(PREFIX)/sbin/update-tcospasswd
	
	# Install tcosxmlrpc utils
	install -m 755 sh/screenshot.sh    $(DESTDIR)/$(TCOS_BINS)/
	install -m 755 sh/soundctl.sh      $(DESTDIR)/$(TCOS_BINS)/
	install -m 755 sh/starthttpd.sh    $(DESTDIR)/$(TCOS_BINS)/
	install -m 755 sh/getinfo.sh       $(DESTDIR)/$(TCOS_BINS)/
	install -m 755 sh/useallmodules.sh $(DESTDIR)/$(TCOS_BINS)/
	install -m 755 sh/devicesctl.sh    $(DESTDIR)/$(TCOS_BINS)/

	install -m 644 var/etc/httpd2.conf $(DESTDIR)/$(PREFIX)/share/tcosmonitor/xmlrpc/
	install -m 644 var/etc/mime.types  $(DESTDIR)/$(PREFIX)/share/tcosmonitor/xmlrpc/

	install -m 644 var/etc/abyss.conf  $(DESTDIR)/$(PREFIX)/share/tcosmonitor/xmlrpc/
	sed -i 's/__TCOS_PATH__//g' $(DESTDIR)/$(PREFIX)/share/tcosmonitor/xmlrpc/abyss.conf

	# standalone package
	install -d $(DESTDIR)/$(TCOS_STANDALONE_DIR)
	install -d $(DESTDIR)/$(TCOS_STANDALONE_DIR)/etc
	install -d $(DESTDIR)/$(TCOS_STANDALONE_DIR)/www
	install -d $(DESTDIR)/$(TCOS_STANDALONE_DIR)/log


	install -m 644 var/etc/abyss.conf       $(DESTDIR)/$(TCOS_STANDALONE_DIR)/etc/abyss-standalone.conf
	sed -i 's|__TCOS_PATH__|$(TCOS_STANDALONE_DIR)|g' $(DESTDIR)/$(TCOS_STANDALONE_DIR)/etc/abyss-standalone.conf
	install -m 644 var/etc/mime.types       $(DESTDIR)/$(TCOS_STANDALONE_DIR)/etc/

	install -m 644 var/etc/httpd2.conf $(DESTDIR)/$(TCOS_STANDALONE_DIR)/etc/httpd.conf
