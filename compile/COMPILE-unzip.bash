#!/usr/bin/env bash

cd ${0%/*}
umask 022

rm -f *.o
make -f unix/Makefile generic

ls -l $PWD/unzip
strip $PWD/unzip
ls -l $PWD/unzip
