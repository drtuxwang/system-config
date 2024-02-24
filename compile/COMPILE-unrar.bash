#!/usr/bin/env bash

cd ${0%/*}
umask 022

make -f makefile

ls -l $PWD/unrar
strip $PWD/unrar
ls -l $PWD/unrar
