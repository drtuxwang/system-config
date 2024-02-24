#!/bin/sh

cd ${0%/*}
umask 022

rm -f *.o
unix/configure
make -f unix/Makefile generic

ls -l $PWD/zip
strip $PWD/zip
ls -l $PWD/zip
