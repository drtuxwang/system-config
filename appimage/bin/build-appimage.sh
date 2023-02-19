#!/usr/bin/env bash
#
# Build AppImage using "appimage-builder"
#

set -eu

if [ $# = 0 ]
then
    echo "Usage: $0 <file.yaml>"
    exit 1

elif [ ! "$(appimage-builder -h 2> /dev/null | grep "usage: appimage-builder")" ]
then
    echo "$0: Error: Cannot find \"appimage-builder\" tool"
    exit 1
elif [ ! "$(which patchelf)" ]
then
    echo "$0: Error: Cannot find \"patchelf\" tools"
    exit 1
fi


export PATH="${0%/*}:/usr/lib/x86_64-linux-gnu/glib-2.0:$PATH"
appimage-builder --recipe "$1" --skip-test
