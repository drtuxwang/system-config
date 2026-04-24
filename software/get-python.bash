#!/usr/bin/env bash
#
# Python 3.13.13 (Official) & newer versions source code
#

set -e


source_settings() {
    NAME="python"
    VERSION="3.13.13"
    PORT="source-c"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://www.python.org/ftp/python/$VERSION/Python-$VERSION.tar.xz
    "
    APP_SHELL="
        mv Python-$VERSION/* .
        cp -p ${0%/*}/../compile/COMPILE-python.bash .
        touch -r README.rst COMPILE-python.bash
    "
    APP_REMOVE="
        Python-$VERSION
    "
}

source_settings_3_14() {
    NAME="python"
    VERSION="3.14.4"
    PORT="source-c"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://www.python.org/ftp/python/$VERSION/Python-$VERSION.tar.xz
    "
    APP_SHELL="
        mv Python-$VERSION/* .
        cp -p ${0%/*}/../compile/COMPILE-python.bash .
        touch -r README.rst COMPILE-python.bash
    "
    APP_REMOVE="
        Python-$VERSION
    "
}


source "${0%/*}/setup-software.bash" source_settings
source "${0%/*}/setup-software.bash" source_settings_3_14
