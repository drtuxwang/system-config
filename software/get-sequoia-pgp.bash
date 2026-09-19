#!/usr/bin/env bash
#
# Sequoia PGP 1.4.0 (Debian 14) portable app
# - Requires: bwrap (Bubblewrap)
#

set -e


app_settings() {
    NAME="sequoia-pgp"
    VERSION="1.4.0"
    PORT="linux64-x86-glibc_2.41"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    REPO="https://deb.debian.org/debian/pool"
    APP_FILES="
        $REPO/main/r/rust-sequoia-sq/sq_1.4.0-1_amd64.deb
    "
    APP_SHELL="
        mv usr/bin/sq .
    "
    APP_REMOVE="
        usr/
    "
}


source "${0%/*}/setup-software.bash" "$@" app_settings
