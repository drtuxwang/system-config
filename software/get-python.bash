#!/usr/bin/env bash
#
# Python 3.14.6 (Official) & newer versions source code
#

set -e


source_settings() {
    NAME="python"
    VERSION="3.14.6"
    PORT="source-c"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://www.python.org/ftp/python/$VERSION/Python-$VERSION.tar.xz
        ${0%/*}/../compile/COMPILE-python.bash
    "
    APP_SHELL="
        mv Python-$VERSION/* .
        touch -r README.rst COMPILE-python.bash
    "
    APP_REMOVE="
        Python-$VERSION
    "
}


source "${0%/*}/setup-software.bash" "$@" source_settings
