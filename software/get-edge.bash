#!/usr/bin/env bash
#
# Edge 144.0.3719.115 (Official) portable app
#

set -e


app_settings() {
    NAME="edge"
    VERSION="144.0.3719.115-1"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_${VERSION%-*}-$PORT"
    APP_FILES="
        https://packages.microsoft.com/repos/edge/pool/main/m/microsoft-edge-stable/microsoft-edge-stable_${VERSION}_amd64.deb
    "
    APP_REMOVE="
        etc/
        opt/microsoft/msedge/AdSelectionAttestationsPreloaded/
        opt/microsoft/msedge/cron/
        usr/
    "
    APP_SHELL="
        mv opt/microsoft/msedge/* .
        rm -r opt/
    "
    APP_START="microsoft-edge"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    exec "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" app
