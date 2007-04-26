
CFLAGS=-Wall -ansi -pedantic `xmlrpc-c-config abyss-server --cflags`

LIBS=`xmlrpc-c-config abyss-server --libs` -lcrypt -lX11

DEFINES= -DBSIZE=512
TEST_DEFINES=-DDEBUG -DBSIZE=512 -DVISIBLE_PASSWD

GCC=gcc

SERVER=tcosxmlrpc


all: server tcospasswd 

server:
	$(GCC) $(DEFINES) -o $(SERVER) $(CFLAGS) $(LIBS) $(SERVER).c

debug:
	$(GCC) $(TEST_DEFINES) -o $(SERVER) $(CFLAGS) $(LIBS) $(SERVER).c



validate-tcos:
	$(GCC) $(DEFINES) -o validate-tcos $(CFLAGS) $(LIBS) validate-tcos.c

tcospasswd:
	$(GCC) $(DEFINES) -o tcospasswd tcospasswd.c -lcrypt

#tcosmd5:
#	cd md5 && make md5c.o
#	$(GCC) -o tcosmd5 tcosmd5.c $(MD5)

clean:
#	cd md5 && make clean
	rm -f $(SERVER) tcosmd5 prueba prueba2 prueba3 validate-tcos tcospasswd var/log.txt var/log/* *~

run:
	./$(SERVER) var/etc/abyss.conf

#debug:
#	XMLRPC_TRACE_XML=1 XMLRPC_TRACE_ABYSS=1 ABYSS_TRACE_CONN=1 ABYSS_TRACE_SOCKET=1 ./$(SERVER) var/etc/abyss.conf

client:
	python2.4 test/client.py

kill:
	killall $(SERVER) ; true
