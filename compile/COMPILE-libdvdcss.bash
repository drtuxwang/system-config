#!/bin/sh

cd ${0%/*}
umask 022

rm -f `find . | egrep "[.]o$|[.]lo$"`
./configure
make

ln -sf libdvdcss.so.2.1.0 .libs/libdvdcss.so
ln -sf libdvdcss.so.2.1.0 .libs/libdvdcss.so.2

echo "Copy to \"/usr/lib\" to install"
ls -l $PWD//.libs/libdvdcss.so*
