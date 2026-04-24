#!/usr/bin/env bash
#
# Instant Client 23.26.1 (Official) library & portable app
# - Requires: libaio1 from Debian 10
#

set -e


app_settings() {
    NAME="instant-client"
    VERSION="23.26.1.0.0"
    PORT="linux64-x86-glibc_2.28"

    APP_DIRECTORY="${NAME}_${VERSION%.*.*}-$PORT"
    REPO1="https://download.oracle.com/otn_software/linux/instantclient"
    REPO2="https://archive.debian.org/debian/pool"
    APP_FILES="
        $REPO1/${VERSION//./}/instantclient-basiclite-linux.x64-$VERSION.zip
        $REPO1/${VERSION//./}/instantclient-sqlplus-linux.x64-$VERSION.zip
        $REPO2/main/liba/libaio/libaio1_0.3.112-3_amd64.deb
    "
    APP_SHELL="
        mv instantclient_* bin/
        ln -s bin lib
        cp ${0%.*}/sqlnet.ora .
        touch -r bin/sqlplus sqlnet.ora
    "
    APP_REMOVE="
        META-INF
        usr/share/
    "
    APP_START="bin/sqlplus"
    APP_LINK="sqlplus64"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    # Python cx_Oracle requires sqlplus run times. Set ORACLE_HOME this directory to work.
    export ORACLE_HOME="$MYDIR"
    export TNS_ADMIN="$MYDIR/sqlnet.ora"
    export LD_LIBRARY_PATH="$MYDIR/lib:$MYDIR/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
    exec "$MYDIR/bin/sqlplus" "$@"
}


source "${0%/*}/setup-software.bash" app_settings
