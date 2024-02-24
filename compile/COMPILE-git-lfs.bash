#!/usr/bin/env bash

cd ${0%/*}
umask 022

make

cp -p CHANGELOG.md README.md bin/

ls -l $PWD/bin/*
