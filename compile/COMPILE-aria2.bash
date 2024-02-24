#!/usr/bin/env bash

cd ${0%/*}
umask 022

case $(uname) in
Darwin)
    export CPPFLAGS="-I/usr/local/opt/libxml2/include $CPPFLAGS"
    export LDFLAGS="-L/usr/local/opt/libxml2/lib $LDFALGS"
    export PKG_CONFIG_PATH="/usr/local/opt/libxml2/lib/pkgconfig:$PKG_CONFIG_PATH"
    ;;
esac

./configure
make

ls -l $PWD/src/aria2c
strip $PWD/src/aria2c
ls -l $PWD/src/aria2c
