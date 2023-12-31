#!/usr/bin/env bash

umask 022
./autogen.sh
./configure
make

ls -l tmux
strip tmux
ls -l tmux
