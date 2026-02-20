#!/usr/bin/env bash
#
# Python 3.13.12 (Official) source code
#

set -e


source_settings() {
    NAME="python"
    VERSION="3.9.25"
    PORT="source-c"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://www.python.org/ftp/python/$VERSION/Python-$VERSION.tar.xz
    "
    APP_SHELL="
        mv Python-$VERSION/* .
        rm -rf Python-$VERSION
        cp -p ${0%/*}/../compile/COMPILE-python3.8-3.10.bash COMPILE-python${VERSION%.*}.bash
        touch -r README.rst COMPILE-python${VERSION%.*}.bash
    "
}


source "${0%/*}/setup-software.bash" source_settings
