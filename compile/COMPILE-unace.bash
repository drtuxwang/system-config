#!/usr/bin/env bash

cd ${0%/*}
umask 022

./configure
make

ls -l $PWD/src/unace
strip $PWD/src/unace
ls -l $PWD/src/unace
