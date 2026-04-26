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
        $REPO/main/e/efivar/libefiboot1t64_38-3.1+b1_amd64.deb
        $REPO/main/e/efivar/libefivar1t64_38-3.1+b1_amd64.deb
        $REPO/main/g/glibc/libc6_2.41-12+deb13u2_amd64.deb
        $REPO/main/g/grub2/grub-pc-bin_2.12-9+deb13u1_amd64.deb
        $REPO/main/g/grub2/grub2-common_2.12-9+deb13u1_amd64.deb
        $REPO/main/l/lvm2/libdevmapper1.02.1_1.02.205-2_amd64.deb
        $REPO/main/libc/libcap2/libcap2_2.75-10+b8_amd64.deb
        $REPO/main/libs/libselinux/libselinux1_3.8.1-1_amd64.deb
        $REPO/main/p/pcre2/libpcre2-8-0_10.46-1~deb13u1_amd64.deb
        $REPO/main/s/systemd/libudev1_257.9-1~deb13u1_amd64.deb
        $REPO/main/x/xz-utils/liblzma5_5.8.1-1_amd64.deb
    "
    APP_SHELL="
        mkdir -p grub-pc
        mv usr/sbin/grub-install grub-pc/
        mv usr/lib/grub/i386-pc/ grub-pc/
        mv usr/lib/x86_64-linux-gnu/libc.so.6 grub-pc/
        mv usr/lib/x86_64-linux-gnu/libcap.so.2.* grub-pc/libcap.so.2
        mv usr/lib/x86_64-linux-gnu/libdevmapper.so.1.* grub-pc/
        mv usr/lib/x86_64-linux-gnu/libefiboot.so.1.* grub-pc/libefiboot.so.1
        mv usr/lib/x86_64-linux-gnu/libefivar.so.1.* grub-pc/libefivar.so.1
        mv usr/lib/x86_64-linux-gnu/liblzma.so.5.* grub-pc/liblzma.so.5
        mv usr/lib/x86_64-linux-gnu/libm.so.6 grub-pc/
        mv usr/lib/x86_64-linux-gnu/libpcre2-8.so.0.* grub-pc/libpcre2-8.so.0
        mv usr/lib/x86_64-linux-gnu/libselinux.so.1 grub-pc/
        mv usr/lib/x86_64-linux-gnu/libudev.so.1.* grub-pc/libudev.so.1
        cp ${0%.*}/grub.cfg grub-pc/
        cp ${0%.*}/README-grub-pc.md grub-pc/
        cp ${0%.*}/install-grub-pc.bash grub-pc/
        touch -r grub-pc/grub-install README-grub-pc.md install-grub-pc.bash grub-pc/grub.cfg
        export XZ_OPT='-9 -e --x86 --lzma2=dict=128MiB --threads=1'
        tar cfJ - grub-pc --owner=0:0 --group=0:0 >> install-grub-pc.bash
        touch -r grub-pc/grub-install install-grub-pc.bash
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
        mv usr/sbin/grub-install grub-pc/
        mv usr/lib/grub/i386-pc/ grub-pc/
        mv usr/lib/x86_64-linux-gnu/libefiboot.so.1.* grub-pc/libefiboot.so.1
        mv usr/lib/x86_64-linux-gnu/libefivar.so.1.* grub-pc/libefivar.so.1
        cp ${0%.*}/grub.cfg grub-pc/
        cp ${0%.*}/README-grub-pc.md-deb11 grub-pc/
        cp ${0%.*}/install-grub-pc.bash grub-pc/
        touch -r grub-pc/grub-install README-grub-pc.md install-grub-pc.bash grub-pc/grub.cfg
        export XZ_OPT='-9 -e --x86 --lzma2=dict=128MiB --threads=1'
        tar cfJ - grub-pc --owner=0:0 --group=0:0 >> install-grub-pc.bash
        touch -r grub-pc/grub-install install-grub-pc.bash
    "
    APP_REMOVE="
        etc/
        grub-pc/
        usr/
    "
}


source "${0%/*}/setup-software.bash" app_settings app_settings_deb11
