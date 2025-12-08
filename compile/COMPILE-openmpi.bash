#!/usr/bin/env bash

THREADS=$(awk '/processor/ {n++} END {print n/2+1}' /proc/cpuinfo 2> /dev/null)

cd ${0%/*}
umask 022

if [[ ${0##/*} =~ COMPILE32* ]]
then
    CC="gcc"; CFLAGS="-fPIC -m32"; export CC CFLAGS
    CXX="g++"; CXXFLAGS="-fPIC -m32"; export CXX CXXFLAGS
    FC="gfortran"; FFLAGS="-fPIC -m32 -fno-second-underscore"; export FC FFLAGS
else
    CC="gcc"; CFLAGS="-fPIC"; export CC CFLAGS
    CXX="g++"; CXXFLAGS="-fPIC"; export CXX CXXFLAGS
    FC="gfortran"; FFLAGS="-fPIC -fno-second-underscore"; export FC FFLAGS
fi

./configure --prefix="$PWD/install"
make -j $THREADS
make install

ls -ld $PWD/install/* $PWD/install/bin/*
