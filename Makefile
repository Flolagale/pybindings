# Simple makefile to compile and link the test classes for the pybinding project.
CC=g++
CFLAGS=-W -Wall -ansi -pedantic -fPIC
LDFLAGS=

all: pynding

pynding: *.h *.cpp
	$(CC) $(CFLAGS) -shared *.h *.cpp -o libpynding.so

clean:
	rm *.o

mrproper: clean
	rm pynding.so
