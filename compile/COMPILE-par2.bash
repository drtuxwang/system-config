#!/usr/bin/env bash

cd ${0%/*}
umask 022

aclocal
automake --add-missing
autoconf
./configure
make

ls -l $PWD/par2
strip $PWD/par2
ls -l $PWD/par2
