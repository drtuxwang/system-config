#!/usr/bin/env bash

THREADS=$(awk '/processor/ {n++} END {print n/2+1}' /proc/cpuinfo 2> /dev/null)

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
make -j $THREADS

ls -l $PWD/src/aria2c
strip $PWD/src/aria2c
ls -l $PWD/src/aria2c
