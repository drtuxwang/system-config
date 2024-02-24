#!/usr/bin/env bash

cd ${0%/*}
umask 022

make

cp -p LICENSE README.md bin/

ls -l $PWD/bin/*
