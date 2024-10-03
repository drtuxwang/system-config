#!/usr/bin/env bash

cd ${0%/*}
umask 022

# Re-direct Golang compiler download
export HOME=$PWD/home

make

cp -p LICENSE README.md bin/
chmod -R u+w .

ls -l $PWD/bin/*
