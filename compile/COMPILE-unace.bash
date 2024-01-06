#!/usr/bin/env bash

umask 022
./configure
make

ls -l ./src/unace
strip ./src/unace
ls -l ./src/unace
