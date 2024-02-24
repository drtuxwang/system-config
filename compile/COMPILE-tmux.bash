#!/usr/bin/env bash

cd ${0%/*}
umask 022

./autogen.sh
./configure
make

ls -l $PWD/tmux
strip $PWD/tmux
ls -l $PWD/tmux
