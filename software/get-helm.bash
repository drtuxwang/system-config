#!/usr/bin/env bash
#
# Helm 3.19.5 (Official) source code & Linux portable app
#

set -e


source_settings() {
    NAME="helm"
    VERSION="3.19.5"
    PORT="source-golang"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://github.com/helm/helm/archive/refs/tags/v$VERSION.tar.gz
    "
    APP_SHELL="
        mv helm-$VERSION/* .
        rm -rf helm-$VERSION/
        cp -p ${0%/*}/../compile/COMPILE-helm.bash .
        touch -r README.md COMPILE-helm.bash
    "
}

app_settings() {
    NAME="helm"
    VERSION="3.19.5"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://get.helm.sh/helm-v$VERSION-linux-amd64.tar.gz
    "
    APP_SHELL="
        mv linux-amd64/* .
        rmdir linux-amd64/
    "
    APP_START="helm"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    exec "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" source_settings app_settings
