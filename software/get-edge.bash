#!/usr/bin/env bash
#
# Edge 146.0.3856.97 (Official) portable app
#

set -e


app_settings() {
    NAME="edge"
    VERSION="146.0.3856.97-1"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_${VERSION%-*}-$PORT"
    REPO="https://packages.microsoft.com/repos/edge/pool"
    APP_FILES="
        $REPO/main/m/microsoft-edge-stable/microsoft-edge-stable_${VERSION}_amd64.deb
    "
    APP_SHELL="
        mv opt/microsoft/msedge/* .
        rm -r opt/
        find locales -type f -not -name en-* -exec rm -v {} +
    "
    APP_REMOVE="
        _gpgorigin
        etc/
        cron/
        MEIPreload/
        WidevineCdm/
        usr/
    "
    APP_START="microsoft-edge"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    exec "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" app_settings
