#!/usr/bin/env bash

umask 022
./configure
make

ls -l src/xz/.libs/xz
ls -l src/liblzma/.libs/liblzma.so.5*
strip src/xz/.libs/xz
ls -l src/xz/.libs/xz
ls -l src/liblzma/.libs/liblzma.so.5*
