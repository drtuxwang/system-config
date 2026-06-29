#!/usr/bin/env bash
#
# GRUB EFI 2.12 (Debian 13) boot loader
# - Requires: shim-signed from Debian Sid (supports both Microsoft CA 2011 and 2023)
#

set -e


app_settings() {
    NAME="grub-efi"
    VERSION="2.12"
    PORT="boot64-x86"
    ARCH="x64"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    REPO="https://deb.debian.org/debian/pool"
    APP_FILES="
        $REPO/main/g/grub-efi-amd64-signed/grub-efi-amd64-signed_1+2.12+9+deb13u2_amd64.deb
        $REPO/main/s/shim-helpers-amd64-signed/shim-helpers-amd64-signed_1+15.8+1_amd64.deb
        $REPO/main/s/shim-signed/shim-signed_1.50+16.1-2_amd64.deb
        ${0%/*}/files/grub.cfg
        ${0%/*}/files/install-grub-efi.bash
        ${0%/*}/files/README-grub-efi.md
    "
    APP_SHELL="
        mkdir -p EFI/boot EFI/debian
        mv usr/lib/shim/shim$ARCH.efi.signed EFI/boot/boot$ARCH.efi
        mv usr/lib/grub/*-efi-signed/grub$ARCH.efi.signed EFI/boot/grub$ARCH.efi
        mv usr/lib/shim/mm$ARCH.efi.signed EFI/boot/mm$ARCH.efi
        mv grub.cfg EFI/debian/
        touch -r EFI/boot/boot*.efi README-grub-efi.md install-grub-efi.bash EFI/debian/grub.cfg
    "
    APP_REMOVE="
        usr/
    "
}

app_settings_arm() {
    NAME="grub-efi"
    VERSION="2.12"
    PORT="boot64-arm"
    ARCH="aa64"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    REPO="https://deb.debian.org/debian/pool"
    APP_FILES="
        $REPO/main/g/grub-efi-arm64-signed/grub-efi-arm64-signed_1+2.12+9+deb13u2_arm64.deb
        $REPO/main/s/shim-helpers-arm64-signed/shim-helpers-arm64-signed_1+15.8+1_arm64.deb
        $REPO/main/s/shim-signed/shim-signed_1.50+16.1-2_arm64.deb
        ${0%/*}/files/grub.cfg-arm
        ${0%/*}/files/install-grub-efi.bash
        ${0%/*}/files/README-grub-efi.md-arm
    "
    APP_SHELL="
        mkdir -p EFI/boot EFI/debian
        mv usr/lib/shim/shim$ARCH.efi.signed EFI/boot/boot$ARCH.efi
        mv usr/lib/grub/*-efi-signed/grub$ARCH.efi.signed EFI/boot/grub$ARCH.efi
        mv usr/lib/shim/mm$ARCH.efi.signed EFI/boot/mm$ARCH.efi
        mv grub.cfg-arm EFI/debian/grub.cfg
        mv README-grub-efi.md-arm README-grub-efi.md
        touch -r EFI/boot/boot*.efi README-grub-efi.md install-grub-efi.bash EFI/debian/grub.cfg
    "
    APP_REMOVE="
        usr/
    "
}


source "${0%/*}/setup-software.bash" "$@" app_settings app_settings_arm
