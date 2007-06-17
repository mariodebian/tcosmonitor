PROGRAMS = lockscreen
SOURCES = lockscreen2.c
LOCKSCREEN_FILE=/usr/share/tcosmonitor/xmlrpc/locked.png
LDADD = -Wall -DLOCKSCREEN_IMAGE=\"$(LOCKSCREEN_FILE)\" -L/usr/lib/ -lXaw -lImlib -lX11 -lXext -ljpeg -lpng


all: compile

include ../common.mk


compile:
	$(CC) $(SOURCES) $(LDADD) -o $(PROGRAMS)

clean:
	rm -f $(PROGRAMS) *~

debug: clean
	$(CC) $(SOURCES) $(LDADD) -o $(PROGRAMS) -DDEBUG=1 -DLOCKSCREEN_IMAGE=\"lockscreen.png\"

