#!/usr/bin/env bash

THREADS=$(awk '/processor/ {n++} END {print n/2+1}' /proc/cpuinfo 2> /dev/null)

cd ${0%/*}
umask 022

if [ $(uname) = Darwin ]
then
    ./configure --enable-utf8proc
else
    ./configure
fi
make -j $THREADS

ls -l $PWD/tmux
strip $PWD/tmux
ls -l $PWD/tmux
