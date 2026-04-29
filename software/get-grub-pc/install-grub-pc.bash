#!/usr/bin/env bash
#
# Install MBR boot sector & stage 2 files for BIOS booting (non EFI)
#

set -eu


extract() {
    DIR="$1"
    rm -rf $DIR/grub-pc
    mkdir -p $DIR/grub-pc

    LINE=$(grep -a -n "^### TAR.XZ PAYLOAD ###$" "$0" | cut -f1 -d:)
    BYTES=$(head -n $LINE "$0" | wc -c)
    echo
    echo "dd ibs=$BYTES skip=1 if=\"$0\" | tar xfJ - -C $DIR"
    dd ibs=$BYTES skip=1 if="$0" 2> /dev/null | tar xfJ - -C $DIR || exit 1
}


autorun() {
    GRUB=$1

    DEVICE=$(df . | grep /dev/ | sed -e "s/[0-9]* .*//")
    if [ ! "$DEVICE" ]
    then
        echo "Cannot detect removable drive device name."
        exit 1
    fi

    echo
    echo "Install GRUB on $DEVICE & copy files to $INSTALL/boot/grub? (y/n)"
    read ANSWER
    if [ "$ANSWER" != y ]
    then
         exit 1
    fi

    echo "rm -rf \"$INSTALL/boot/grub/i386-pc\""
    rm -rf "$INSTALL/boot/grub/i386-pc"
    export LD_LIBRARY_PATH="$GRUB:${LD_LIBRARY_PATH:-}"
    echo "$GRUB/grub-install --directory=$GRUB/i386-pc --boot-directory=\"$INSTALL/boot\" $DEVICE"
    $GRUB/grub-install --directory=$GRUB/i386-pc --boot-directory="$INSTALL/boot" $DEVICE
    rm -rf $INSTALL/boot/grub/fonts $INSTALL/boot/grub/locale

    if [ -f "$INSTALL/EFI/debian/grub.cfg" ]
    then
        echo "cp -p \"$INSTALL/EFI/debian/grub.cfg\" \"$INSTALL/boot/grub/grub.cfg\""
        sed -e "1,18s/EFI/BIOS/"  "$INSTALL/EFI/debian/grub.cfg" > "$INSTALL/boot/grub/grub.cfg"
        touch -r "$INSTALL/EFI/debian/grub.cfg" "$INSTALL/boot/grub/grub.cfg"
    elif [ ! -f "$INSTALL/boot/grub/grub.cfg" ]
    then
        echo "cp -p $GRUB/grub.cfg \"$INSTALL/boot/grub/grub.cfg\""
        cp -p $GRUB/grub.cfg "$INSTALL/boot/grub/grub.cfg"
    fi
}


ARG=${1:-}
if [ "$ARG" = "-x" ]
then
    extract .
    du -sk grub-pc
    exit
elif [ ! -d "${1:-}" ]
then
    echo "Usage $0 <boot-mountpoint>"
    echo "      $0 -x"
    exit 1
fi

MYUNAME=`id | sed -e 's/^[^(]*(\([^)]*\)).*$/\1/'`
[ "$MYUNAME" != root ] && exec sudo sh $0 "$@"

INSTALL=$(df $1 | awk 'NR==2 {print $NF}')
umask 022
[ "$(cmp "README-grub-pc.md" "$INSTALL/README-grub-pc.md" 2>&1)" ] && \
    cp README-grub-pc.md "$INSTALL" && \
    touch -r README-grub-pc.md "$INSTALL/README-grub-pc.md"
umask 077
extract /tmp/$MYUNAME
cd "$INSTALL"
autorun /tmp/$MYUNAME/grub-pc
echo "rm -rf /tmp/$MYUNAME/grub-pc"
rm -rf /tmp/$MYUNAME/grub-pc

echo "DONE!"
exit
### TAR.XZ PAYLOAD ###
