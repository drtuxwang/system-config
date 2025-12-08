#!/usr/bin/env bash

THREADS=$(awk '/processor/ {n++} END {print n/2+1}' /proc/cpuinfo 2> /dev/null)

cd ${0%/*}
umask 022

./configure
make -j $THREADS

ls -l $PWD/programs/zstd
strip $PWD/programs/zstd
ls -l $PWD/programs/zstd
