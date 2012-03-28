# Simple makefile to compile and link the test classes for the pybinding project.
CC=g++
CFLAGS=-W -Wall -ansi -pedantic -fPIC
LDFLAGS=

all: pyndings

pyndings: *.h *.cpp
	$(CC) $(CFLAGS) -shared *.h *.cpp -o libpyndings.so

clean:
	rm *.o libpyndings.so

