#!/usr/bin/env bash

umask 022
./configure
(cd src; make)

ls -l src/tinyproxy
strip src/tinyproxy
ls -l src/tinyproxy
