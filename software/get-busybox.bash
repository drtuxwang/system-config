#!/usr/bin/env bash
#
# 7-Zip 26.00 (Official) source code & Windows portable app
#

set -e


windows_settings() {
    NAME="busybox"
    VERSION="1.37.0"
    PORT="windows64-x86"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://frippery.org/files/busybox/busybox-w64-FRP-5467-g9376eebd8.exe
        ${0%/*}/files/busybox.bat
        ${0%/*}/files/init-ash
        ${0%/*}/files/sysinfo
        ${0%/*}/files/sysinfo.py
        ${0%/*}/files/sysinfo.sh
        ${0%/*}/files/uname
        ${0%/*}/files/vi
        ${0%/*}/files/vim
    "
    APP_SHELL="
        mkdir -p bin etc ../bin
        sed -e 's/\x00uname\x00/\x00unam#\x00/;s/\x00vi\x00watch\x00/\x00v#\x00watch\x00/' \
            busybox-*.exe > busybox.exe
        mv sysinfo* uname vi* bin/
        mv init-ash etc/
        sed -e 's/{{ version }}/$VERSION/' ${0%.*}/busybox.bat-bin > ../bin/busybox.bat
        chmod 755 busybox.exe ../bin/busybox.bat
        touch -r busybox-*.exe busybox.exe busybox.bat bin/* etc/* ../bin/busybox.bat ../bin
        rm busybox-*.exe
    "
}

windows_settings_32bit() {
    NAME="busybox"
    VERSION="1.37.0"
    PORT="windows-x86"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://frippery.org/files/busybox/busybox-w32-FRP-5467-g9376eebd8.exe
        ${0%/*}/files/busybox.bat
        ${0%/*}/files/init-ash
        ${0%/*}/files/sysinfo
        ${0%/*}/files/sysinfo.py
        ${0%/*}/files/sysinfo.sh
        ${0%/*}/files/uname
        ${0%/*}/files/vi
        ${0%/*}/files/vim
    "
    APP_SHELL="
        mkdir -p bin etc ../bin
        sed -e 's/\x00uname\x00/\x00unam#\x00/;s/\x00vi\x00watch\x00/\x00v#\x00watch\x00/' \
            busybox-*.exe > busybox.exe
        mv sysinfo* uname vi* bin/
        mv init-ash etc/
        sed -e 's/{{ version }}/$VERSION/' ${0%.*}/busybox.bat-bin > ../bin/busybox.bat
        chmod 755 busybox.exe ../bin/busybox.bat
        touch -r busybox-*.exe busybox.exe busybox.bat bin/* etc/* ../bin/busybox.bat ../bin
        rm busybox-*.exe
    "
}


app_start() {
    MYDIR=$(realpath "${0%/*}")
    exec "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" "$@" windows_settings windows_settings_32bit
