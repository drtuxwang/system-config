#!/usr/bin/env bash
#
# GRUB PC 2.12 (Debian 13) boot loader
#

set -e


app_settings() {
    NAME="grub-pc"
    VERSION="2.12"
    PORT="linux-x86-glibc_2.41"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    REPO="https://deb.debian.org/debian/pool"
    APP_FILES="
        $REPO/main/g/grub2/grub-pc-bin_2.12-9+deb13u1_amd64.deb
        $REPO/main/g/grub2/grub2-common_2.12-9+deb13u1_amd64.deb
        $REPO/main/e/efivar/libefiboot1t64_38-3.1+b1_amd64.deb
        $REPO/main/e/efivar/libefivar1t64_38-3.1+b1_amd64.deb
    "
    APP_SHELL="
        mkdir -p grub-pc
        mv usr/sbin/grub-install grub-pc/
        mv usr/lib/grub/i386-pc/ grub-pc/
        mv usr/lib/x86_64-linux-gnu/libefiboot.so.1.* grub-pc/libefiboot.so.1
        mv usr/lib/x86_64-linux-gnu/libefivar.so.1.* grub-pc/libefivar.so.1
        cp ${0%.*}/grub.cfg grub-pc/
        cp ${0%.*}/README-grub-pc.md .
        cp ${0%.*}/install-grub-pc.bash .
        touch -r grub-pc/grub-install grub-pc/grub.cfg
        export XZ_OPT='-9 -e --x86 --lzma2=dict=128MiB --threads=1'
        tar cfJ - grub-pc --owner=0:0 --group=0:0 >> install-grub-pc.bash
        touch -r grub-pc/grub-install README-grub-pc.md install-grub-pc.bash
    "
    APP_REMOVE="
        etc/
        grub-pc/
        usr/
    "
}

app_settings_deb11() {
    NAME="grub-pc"
    VERSION="2.06"
    PORT="linux-x86-glibc_2.31"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    REPO="https://deb.debian.org/debian/pool"
    APP_FILES="
        $REPO/main/g/grub2/grub-pc-bin_2.06-3~deb11u6_amd64.deb
        $REPO/main/g/grub2/grub2-common_2.06-3~deb11u6_amd64.deb
        $REPO/main/e/efivar/libefiboot1_37-6_amd64.deb
        $REPO/main/e/efivar/libefivar1_37-6_amd64.deb
    "
    APP_SHELL="
        mkdir -p grub-pc
        mv usr/sbin/grub-install grub-pc
        mv usr/lib/grub/i386-pc/ grub-pc/
        mv usr/lib/x86_64-linux-gnu/libefiboot.so.1.* grub-pc/libefiboot.so.1
        mv usr/lib/x86_64-linux-gnu/libefivar.so.1.* grub-pc/libefivar.so.1
        cp ${0%.*}/grub.cfg grub-pc/
        cp ${0%.*}/README-grub-pc.md-deb11 README-grub-pc.md
        cp ${0%.*}/install-grub-pc.bash .
        touch -r grub-pc/grub-install grub-pc/grub.cfg
        export XZ_OPT='-9 -e --x86 --lzma2=dict=128MiB --threads=1'
        tar cfJ - grub-pc --owner=0:0 --group=0:0 >> install-grub-pc.bash
        touch -r grub-pc/grub-install README-grub-pc.md install-grub-pc.bash
    "
    APP_REMOVE="
        etc/
        grub-pc/
        usr/
    "
}


source "${0%/*}/setup-software.bash" app_settings app_settings_deb11
