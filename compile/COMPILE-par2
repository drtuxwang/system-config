#!/usr/bin/env bash

umask 022
aclocal
automake --add-missing
autoconf
./configure
make

ls -l par2
strip par2
ls -l par2
