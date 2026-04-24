#!/usr/bin/env bash
#
# Install boot files into EFI boot partition for UEFI secure boot
#

set -eu


install() {
    SOURCE="$1"
    TARGET="$2"
    mkdir -p "$TARGET"

    for FILE in $(ls -1 $SOURCE)
    do
        if [ "$(cmp "$SOURCE/$FILE" "$TARGET/$FILE" 2>&1)" ]
        then
            echo "cp -p \"$SOURCE/$FILE\" \"$TARGET/$FILE\""
            cp "$SOURCE/$FILE" "$TARGET/$FILE"
            touch -r "$SOURCE/$FILE" "$TARGET/$FILE"
        fi
    done
}


if [ $# != 1 -o ! -d "${1:-}" ]
then
    echo "Usage $0 <efi-mountpoint>"
    exit 1
fi

MYUNAME=`id | sed -e 's/^[^(]*(\([^)]*\)).*$/\1/'`
[ "$MYUNAME" != root ] && exec sudo sh "$0" "$@"

echo "Updating EFI partition: $1"
MYDIR=$(readlink -m "${0%/*}")
install "$MYDIR/EFI/boot" "$1/EFI/boot"
[ ! -d "$1/EFI/debian" ] && install "$MYDIR/EFI/debian" "$1/EFI/debian"

echo "DONE!"
