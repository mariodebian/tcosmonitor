PROGRAMS = lockscreen
SOURCES = lockscreen.c
#LDADD = -L/usr/X11R6/lib/ -lXaw
LDADD = -L/usr/lib/ -lXaw


all: compile

include ../common.mk


compile:
	$(CC) $(SOURCES) $(LDADD) -o $(PROGRAMS)

clean:
	rm -f $(PROGRAMS)
