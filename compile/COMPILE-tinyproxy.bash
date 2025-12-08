#!/usr/bin/env bash

THREADS=$(awk '/processor/ {n++} END {print n/2+1}' /proc/cpuinfo 2> /dev/null)

cd ${0%/*}
umask 022

./configure
(cd src; make -j $THREADS)

ls -l $PWD/src/tinyproxy
strip $PWD/src/tinyproxy
ls -l $PWD/src/tinyproxy
