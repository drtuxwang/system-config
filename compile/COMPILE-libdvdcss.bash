#!/bin/sh

umask 022
rm -f `find . | egrep "[.]o$|[.]lo$"`
./configure
make

echo "Copy to \"/usr/lib\" to install"
ln -sf libdvdcss.so.2.1.0 .libs/libdvdcss.so
ln -sf libdvdcss.so.2.1.0 .libs/libdvdcss.so.2
ls -l .libs/libdvdcss.so*
