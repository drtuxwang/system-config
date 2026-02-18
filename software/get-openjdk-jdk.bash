#!/usr/bin/env bash
#
# OpenJDK JDK 21.0.9 (Official) portable app
#

set -e


app_settings() {
    NAME="openjdk-jdk"
    VERSION="21.0.9_10"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_${VERSION%_*}-$PORT"
    APP_FILES="
        https://github.com/adoptium/temurin${VERSION%%.*}-binaries/releases/download/jdk-${VERSION//_/%2B}/OpenJDK${VERSION%%.*}U-jdk_x64_linux_hotspot_$VERSION.tar.gz
    "
    APP_REMOVE="
        jdk-*/man/
    "
    APP_SHELL="
        mv jdk-*/* .
        rm -r jdk-*/
    "
    APP_START="bin/java"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    exec "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" app_settings
