#!/usr/bin/env bash
#
# Install boot files into EFI system partition for UEFI secure boot
#

set -eu


copy() {
    [ ! "$(cmp "$1" "$2" 2>&1)" ] && return
    mkdir -p "${2/*}"
    echo "cp -p \"$1\" \"$2\""
    cp "$1" "$2"
    touch -r "$1" "$2"
}

install() {
    SOURCE="$1"
    TARGET="$2"
    for FILE in $(ls -1 $SOURCE)
    do
        copy "$SOURCE/$FILE" "$TARGET/$FILE"
    done
}


if [ $# != 1 -o ! -d "${1:-}" ]
then
    echo "Usage $0 <efi-mountpoint>"
    exit 1
fi

MYUNAME=`id | sed -e 's/^[^(]*(\([^)]*\)).*$/\1/'`
[ "$MYUNAME" != root ] && exec sudo sh "$0" "$@"

MYDIR="${0%/*}"
MOUNT=$(df "$1" 2> /dev/null | awk 'END {print $NF}')
echo "Updating EFI system partition: $MOUNT"

copy "$MYDIR/README-grub-efi.md" "$MOUNT/README-grub-efi.md"
install "$MYDIR/EFI/boot" "$MOUNT/EFI/boot"
[ ! -d "$MOUNT/EFI/debian" ] && install "$MYDIR/EFI/debian" "$MOUNT/EFI/debian"

echo "DONE!"
