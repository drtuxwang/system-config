#!/usr/bin/env bash
#
# Edge 151.0.4129.107 (Official) portable app
#

set -e


app_settings() {
    NAME="edge"
    VERSION="151.0.4129.107-1"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_${VERSION%-*}-$PORT"
    REPO="https://packages.microsoft.com/repos/edge/pool"
    APP_FILES="
        $REPO/main/m/microsoft-edge-stable/microsoft-edge-stable_${VERSION}_amd64.deb
    "
    APP_SHELL="
        mv opt/microsoft/msedge/* .
        find locales -type f -not -name en-* -exec rm -v {} +
    "
    APP_REMOVE="
        _gpgorigin
        apparmor.d
        cron/
        etc/
        MEIPreload/
        opt
        WidevineCdm/
        usr/
    "
    APP_START="microsoft-edge"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    exec "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" "$@" app_settings
