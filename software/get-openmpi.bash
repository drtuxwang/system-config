#!/usr/bin/env bash
#
# Open MPI 5.0.10 (Official) source code
#

set -e


source_settings() {
    NAME="openmpi"
    VERSION="5.0.10"
    PORT="source-c"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://download.open-mpi.org/release/open-mpi/v${VERSION%.*}/openmpi-${VERSION}.tar.bz2
        ${0%/*}/../compile/COMPILE-openmpi.bash
    "
    APP_SHELL="
        mv openmpi-*/* .
        touch -r README.md COMPILE-openmpi.bash
    "
    APP_REMOVE="
        openmpi-*/
    "

}


source "${0%/*}/setup-software.bash" "$@" source_settings
