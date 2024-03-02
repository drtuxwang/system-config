#!/usr/bin/env bash

cd ${0%/*}
umask 022

if [ $(uname) = Darwin ]
then
    ./configure --enable-utf8proc
else
    ./configure
fi
make

ls -l $PWD/tmux
strip $PWD/tmux
ls -l $PWD/tmux
