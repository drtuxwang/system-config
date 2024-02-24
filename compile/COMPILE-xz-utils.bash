#!/usr/bin/env bash

cd ${0%/*}
umask 022

./configure
make

ls -l $PWD/src/xz/.libs/xz $PWD/src/liblzma/.libs/liblzma.so.5*
strip $PWD/src/xz/.libs/xz
ls -l $PWD/src/xz/.libs/xz $PWD/src/liblzma/.libs/liblzma.so.5*
