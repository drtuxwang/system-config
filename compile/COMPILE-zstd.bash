#!/usr/bin/env bash

cd ${0%/*}
umask 022

./configure
make

ls -l $PWD/programs/zstd
strip $PWD/programs/zstd
ls -l $PWD/programs/zstd
