
lockscreen_BIN = lockscreen
lockscreen_SOURCES = lockscreen.c
FLAGS = -L/usr/lib/ -lXaw


all: compile


compile:
	$(CC) $(lockscreen_SOURCES) $(FLAGS) -o $(lockscreen_BIN)

clean:
	rm -f $(lockscreen_BIN)
