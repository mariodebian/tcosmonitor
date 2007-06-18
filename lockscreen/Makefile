PROGRAMS = lockscreen
SOURCES = lockscreen2.c
LOCKSCREEN_FILE=/usr/share/tcosmonitor/xmlrpc/locked.png
LIBS=$(shell imlib-config --libs)
CFLAGS=$(shell imlib-config --cflags)
LDADD = -Wall -DLOCKSCREEN_IMAGE=\"$(LOCKSCREEN_FILE)\" -lXaw $(LIBS) $(CFLAGS)


all: compile

include ../common.mk


compile:
	$(CC) $(SOURCES) $(LDADD) -o $(PROGRAMS)

clean:
	rm -f $(PROGRAMS) *~

debug: clean
	$(CC) $(SOURCES) $(LDADD) -o $(PROGRAMS) -DDEBUG=1 -DLOCKSCREEN_IMAGE=\"lockscreen.png\"

