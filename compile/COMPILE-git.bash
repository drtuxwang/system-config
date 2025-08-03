#!/usr/bin/env bash

cd ${0%/*}
umask 022

if [ "$(uname)" = "Darwin" ]
then
    mv INSTALL INSTALL.txt  # INSTALL/install conflict bug
fi

./configure --prefix=$PWD/install
make -i NO_INSTALL_HARDLINKS=YesPlease install

ls -l $PWD/install/bin/*
strip $PWD/install/bin/* 2> /dev/null
ls -l $PWD/install/bin/*
