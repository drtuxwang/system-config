#!/usr/bin/env bash

umask 022
make

cp -p LICENSE README.md bin/
ls -l bin/*
