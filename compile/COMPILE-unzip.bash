#!/usr/bin/env bash

THREADS=$(awk '/processor/ {n++} END {print n/2+1}' /proc/cpuinfo 2> /dev/null)

cd ${0%/*}
umask 022

rm -f *.o
make -f unix/Makefile generic -j $THREADS

ls -l $PWD/unzip
strip $PWD/unzip
ls -l $PWD/unzip
