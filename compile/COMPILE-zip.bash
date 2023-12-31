#!/bin/sh

umask 022
rm -f *.o
unix/configure
make -f unix/Makefile generic

ls -l zip
strip zip
ls -l zip
