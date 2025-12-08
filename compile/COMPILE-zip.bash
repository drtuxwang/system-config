#!/bin/sh

THREADS=$(awk '/processor/ {n++} END {print n/2+1}' /proc/cpuinfo 2> /dev/null)

cd ${0%/*}
umask 022

rm -f *.o
unix/configure
make -f unix/Makefile generic -j $THREADS

ls -l $PWD/zip
strip $PWD/zip
ls -l $PWD/zip
