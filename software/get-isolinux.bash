#!/usr/bin/env bash
#
# ISOLINUX 4.05 (Debian 7) boot loader
#

set -e


app_settings() {
    NAME="isolinux"
    VERSION="4.05"
    PORT="boot-x86"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        http://archive.debian.org/debian/pool/main/s/syslinux/syslinux-common_4.05+dfsg-6+deb7u1_all.deb
    "
    APP_SHELL="
        mkdir isolinux
        mv usr/lib/syslinux/isolinux.bin isolinux/
        mv usr/lib/syslinux/vesamenu.c32 isolinux/
        cp ${0%.*}/isolinux.cfg isolinux/
        cp ${0%.*}/README-isolinux.md .
        cp ${0%.*}/create-boot-iso.bash isolinux/
        touch -r isolinux/isolinux.bin \
            README-isolinux.md isolinux/create-boot-iso.bash isolinux/isolinux.cfg
    "
    APP_REMOVE="
        usr/
    "
}


source "${0%/*}/setup-software.bash" app_settings
