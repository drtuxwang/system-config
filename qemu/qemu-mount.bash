#!/usr/bin/env bash

set -u

MYHNAME=$(uname -n)
MYUNAME=$(id -un)


help() {
    case ${0##*/} in
    *mount*)
        ps -fu root  | grep qemu-nbd | sed -e "s/.*qemu-nbd/qemu-nbd/"
        df /mnt/qemu* 2> /dev/null | grep /mnt/qemu
        ;;
    *umount*)
        echo "Usage: $0 mountpoint"
        ;;
    *)
        echo "Usage: $0 file.qcows2"
        ;;
    esac
    exit 1
}

mount_image() {
    DEVICE=$(lsblk -list -o NAME,SIZE | awk '/nbd.* 0B$/ {print $1; exit}')
    [ ! "$DEVICE" ] && echo "Unable to find unused \"/dev/nbd*\" device" && exit 1
    echo "qemu-nbd --connect /dev/$DEVICE \"$1\" --discard=unmap --detect-zeroes=unmap"

    qemu-nbd --connect /dev/$DEVICE "$1" --discard=unmap --detect-zeroes=unmap
    sleep 0.25
    for PART in $(lsblk -list -o NAME | grep "^${DEVICE}p" | sed -e "s/${DEVICE}p//")
    do
        MOUNT="/mnt/qemu${DEVICE#nbd}p$PART"
        mkdir -p $MOUNT
        mount /dev/${DEVICE}p$PART $MOUNT
        if [ "$(lsblk -list -o "NAME,FSTYPE" | grep -E "${DEVICE}p$PART  *(vfat|ntfs)")" ]
        then
            umount $MOUNT
            mount -o uid=owner,gid=users /dev/${DEVICE}p$PART $MOUNT
        fi
    done
    df /mnt/qemu${DEVICE#nbd}p* | grep /qemu
    return ${DEVICE#nbd}
}

umount_image() {
    if [[ $1 =~ /dev/nbd* ]]
    then
        DEVICE="${1%p*}"
    else
        DEVICE=$(df "$1" | awk '/^\/dev\/nbd/ {print $1; exit}' | sed -e "s/p.*//")
    fi
    [ "$DEVICE" ] || return

    df 2> /dev/null | grep "^${DEVICE}p" | awk '{print $NF}' | xargs -n 1 umount 2> /dev/null
    qemu-nbd --disconnect $DEVICE
}

trim_image() {
    case ${1##*/} in
    *base*)
        ;;
    *)
        echo
        mount_image "$1"
        UNIT=$?
        fstrim -av | grep "/qemu${UNIT}p" | sort -k5
        umount_image /dev/nbd$UNIT
        ;;
    esac
}


[ $# = 0 ] && help

if [ "$MYUNAME" != root ]
then
    echo -e "\033[33mSwitch root@$MYHNAME: sudo \"$0\" \"$@\"\033[0m"
    exec sudo "$0" "$@"
fi

modprobe nbd max_part=8
while [ $# != 0 ]
do
    case ${0##*/} in
    *trim*)
        trim_image "$1"
        ;;
    *umount*)
        echo
        umount_image "$1"
        ;;
    *)
        echo
        mount_image "$1"
        ;;
    esac
    shift
done
