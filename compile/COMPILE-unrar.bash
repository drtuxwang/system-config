#!/usr/bin/env bash

THREADS=$(awk '/processor/ {n++} END {print n/2+1}' /proc/cpuinfo 2> /dev/null)

cd ${0%/*}
umask 022

make -f makefile -j $THREADS

ls -l $PWD/unrar
strip $PWD/unrar
ls -l $PWD/unrar
