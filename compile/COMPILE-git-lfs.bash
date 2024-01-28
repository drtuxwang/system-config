#!/usr/bin/env bash

umask 022
make

cp -p CHANGELOG.md README.md bin/
ls -l bin/*
