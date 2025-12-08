#!/usr/bin/env bash

THREADS=$(awk '/processor/ {n++} END {print n/2+1}' /proc/cpuinfo 2> /dev/null)

cd ${0%/*}
umask 022

aclocal
automake --add-missing
autoconf
./configure
make -j $THREADS

ls -l $PWD/par2
strip $PWD/par2
ls -l $PWD/par2
