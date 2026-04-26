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

MOUNT=$(df "$1" 2> /dev/null | awk 'END {print $NF}')
echo "Updating EFI partition: $MOUNT"
MYDIR="${0%/*}"
install "$MYDIR/boot" "$MOUNT/EFI/boot"
[ ! -d "$MOUNT/EFI/debian" ] && install "$MYDIR/debian" "$MOUNT/EFI/debian"

echo "DONE!"
