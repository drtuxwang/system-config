#!/usr/bin/env bash
#
# Generate ISO image for BIOS boot system (non UEFI)
#

set -eu

DIR=$(realpath "${0%/*}/..")
VERSION=$(awk '/^menu label \^Debian Live / {print $5; exit}' "$DIR/isolinux/isolinux.cfg")
VOLUME="DEBIANLIVE"
FILE="${DIR%/*}/debianlive_${VERSION}_amd64.iso"

echo "Generating ISO boot disk: $FILE"

cd "$DIR/.."
genisoimage \
    -iso-level 3 -joliet-long -rational-rock -input-charset utf-8 \
    -appid GENISOIMAGE-$(genisoimage -version | awk 'NR==1 {print $2}') \
    -eltorito-boot isolinux/isolinux.bin -no-emul-boot -boot-info-table \
    -volid "$VOLUME" \
    -o "$FILE" \
    "$DIR"

touch -r "$DIR/EFI/debian/grub.cfg" "$FILE"

echo "DONE!"
