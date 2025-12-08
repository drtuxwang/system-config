#!/usr/bin/env bash

THREADS=$(awk '/processor/ {n++} END {print n/2+1}' /proc/cpuinfo 2> /dev/null)

cd ${0%/*}
umask 022

if [ "$(uname)" = "Darwin" ]
then
    mv INSTALL INSTALL.txt  # INSTALL/install conflict bug
fi

./configure --prefix=$PWD/install
make -i NO_INSTALL_HARDLINKS=YesPlease install -j $THREADS

ls -l $PWD/install/bin/*
strip $PWD/install/bin/* 2> /dev/null
ls -l $PWD/install/bin/*
