#!/bin/sh

cd ${0%/*}
umask 022

mkdir bin 2> /dev/null

gcc -O dos2unix.c -o bin/dos2unix
gcc -O ftolower.c -o bin/ftolower
gcc -O ftoupper.c -o bin/ftoupper
gcc -O unix2dos.c -o bin/unix2dos
gcc -O wipe.c -o bin/wipe

ls -l $PWD/bin/*
strip $PWD/bin/*
ls -l $PWD/bin/*
