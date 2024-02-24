#!/usr/bin/env bash

cd ${0%/*}
umask 022

./configure
(cd src; make)

ls -l $PWD/src/tinyproxy
strip $PWD/src/tinyproxy
ls -l $PWD/src/tinyproxy
