#!/usr/bin/env bash

umask 022
rm -f *.o
make -f unix/Makefile generic

ls -l unzip
strip unzip
ls -l unzip
