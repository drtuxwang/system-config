#!/usr/bin/env bash

umask 022

if [ "$(uname)" = "Darwin" ]
then
    mv INSTALL INSTALL.txt  # INSTALL/install conflict bug
fi

./configure --prefix=$PWD/install
make -i NO_INSTALL_HARDLINKS=YesPlease install

ls -l install/bin/*
strip install/bin/*
ls -l install/bin/*
