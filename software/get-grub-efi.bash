#!/usr/bin/env bash
#
# GRUB EFI 2.12 (Debian 13) boot loader
#

set -e


app_settings() {
    NAME="grub-efi"
    VERSION="2.12"
    PORT="boot64-x86"
    ARCH=x64

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    REPO="https://deb.debian.org/debian/pool"
    APP_FILES="
        $REPO/main/g/grub-efi-amd64-signed/grub-efi-amd64-signed_1+2.12+9+deb13u1_amd64.deb
        $REPO/main/s/shim-helpers-amd64-signed/shim-helpers-amd64-signed_1+15.8+1_amd64.deb
        $REPO/main/s/shim-signed/shim-signed_1.47+15.8-1_amd64.deb
    "
    APP_SHELL="
        mkdir -p EFI/boot EFI/debian
        mv usr/lib/shim/shim$ARCH.efi.signed EFI/boot/boot$ARCH.efi
        mv usr/lib/grub/*-efi-signed/grub$ARCH.efi.signed EFI/boot/grub$ARCH.efi
        mv usr/lib/shim/mm$ARCH.efi.signed EFI/boot/mm$ARCH.efi
        cp ${0%.*}/grub.cfg EFI/debian/
        cp ${0%.*}/README-grub-efi.md EFI/
        cp ${0%.*}/install-grub-efi.bash EFI/
        touch -r EFI/boot/boot*.efi \
            EFI/debian/grub.cfg EFI/README-grub-efi.md EFI/installgrub-efi.bash
    "
    APP_REMOVE="
        usr/
    "
}

app_settings_arm() {
    NAME="grub-efi"
    VERSION="2.12"
    PORT="boot64-arm"
    ARCH=aa64

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    REPO="https://deb.debian.org/debian/pool"
    APP_FILES="
        $REPO/main/g/grub-efi-arm64-signed/grub-efi-arm64-signed_1+2.12+9+deb13u1_arm64.deb
        $REPO/main/s/shim-helpers-arm64-signed/shim-helpers-arm64-signed_1+15.8+1_arm64.deb
        $REPO/main/s/shim-signed/shim-signed_1.47+15.8-1_arm64.deb
    "
    APP_SHELL="
        mkdir -p EFI/boot EFI/debian
        mv usr/lib/shim/shim$ARCH.efi.signed EFI/boot/boot$ARCH.efi
        mv usr/lib/grub/*-efi-signed/grub$ARCH.efi.signed EFI/boot/grub$ARCH.efi
        mv usr/lib/shim/mm$ARCH.efi.signed EFI/boot/mm$ARCH.efi
        cp ${0%.*}/grub.cfg-arm EFI/debian/grub.cfg
        cp ${0%.*}/README-grub-efi.md-arm EFI/README-grub-efi.md
        cp ${0%.*}/install-grub-efi.bash EFI/
        touch -r EFI/boot/boot*.efi \
            EFI/debian/grub.cfg EFI/README-grub-efi.md EFI/install-grub-efi.bash
    "
    APP_REMOVE="
        usr/
    "
}


source "${0%/*}/setup-software.bash" app_settings app_settings_arm
