#!/bin/sh

THREADS=$(awk '/processor/ {n++} END {print n/2+1}' /proc/cpuinfo 2> /dev/null)

cd ${0%/*}
umask 022

rm -f `find . | egrep "[.]o$|[.]lo$"`
./configure
make -j $THREADS

ln -sf libdvdcss.so.2.1.0 .libs/libdvdcss.so
ln -sf libdvdcss.so.2.1.0 .libs/libdvdcss.so.2

echo "To install copy to \"/usr/lib\":"
ls -l $PWD/.libs/libdvdcss.so*
fmod -R $PWD/.libs/ 2> /dev/null
