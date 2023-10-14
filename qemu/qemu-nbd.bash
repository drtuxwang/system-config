#!/usr/bin/env bash

set -u

MYHNAME=$(uname -n)
MYUNAME=$(id -un)
OWNER=root:root


help() {
    case ${0##*/} in
    *mount*)
        echo
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

snapshot_drive() {
    [ -f "$2" ] && return
    echo -e "\nqemu-img create -F qcow2 -b $(realpath $1) -f qcow2 $2"
    qemu-img create -F qcow2 -b $(realpath $1) -f qcow2 $2
}

mount_image() {
    DEVICE=$(lsblk -list -o NAME,SIZE | awk '/nbd.* 0B$/ {print $1; exit}')
    [ ! "$DEVICE" ] && echo "Unable to find unused \"/dev/nbd*\" device" && exit 1

    echo -e "\nqemu-nbd --connect /dev/$DEVICE \"$1\" --discard=unmap --detect-zeroes=unmap"
    qemu-nbd --connect /dev/$DEVICE "$1" --discard=unmap --detect-zeroes=unmap
    sleep 0.25
    for PART in $(lsblk -list -o NAME | grep "^${DEVICE}p" | sed -e "s/${DEVICE}p//")
    do
        MOUNT="/mnt/qemu${DEVICE#nbd}p$PART"
        mkdir -p $MOUNT
        if [ "$(lsblk -list -o "NAME,FSTYPE" | grep -E "${DEVICE}p$PART  *(vfat|ntfs)")" ]
        then
            echo "mount -o uid=${OWNER%:*},gid=${OWNER#*:},umask=022,fmask=133 /dev/${DEVICE}p$PART $MOUNT"
            mount -o uid=${OWNER%:*},gid=${OWNER#*:},umask=022,fmask=133 /dev/${DEVICE}p$PART $MOUNT
        else
            echo "mount /dev/${DEVICE}p$PART $MOUNT"
            mount /dev/${DEVICE}p$PART $MOUNT
        fi
    done
    df /mnt/qemu${DEVICE#nbd}p* | grep /qemu
    return ${DEVICE#nbd}
}

mount_base_image() {
    DRIVE_TMPDIR="/tmp/qemu-${OWNER%:*}"
    mkdir -p $DRIVE_TMPDIR && chmod go= $DRIVE_TMPDIR
    snapshot_drive $1 $DRIVE_TMPDIR/$1
    chown -R ${OWNER%:*} $DRIVE_TMPDIR

    mount_image $DRIVE_TMPDIR/$1
}

umount_image() {
    if [[ $1 =~ /dev/nbd* ]]
    then
        DEVICE="${1%p*}"
    else
        DEVICE=$(df "$1" | awk '/^\/dev\/nbd/ {print $1; exit}' | sed -e "s/p.*//")
    fi
    [ "$DEVICE" ] || return

    echo
    for MOUNT in $(df 2> /dev/null | grep "^${DEVICE}p" | awk '{print $NF}')
    do
        echo "umount $MOUNT"
        umount $MOUNT
    done
    qemu-nbd --disconnect $DEVICE
}

trim_image() {
    case ${1##*/} in
    *base*)
        ;;
    *)
        mount_image "$1"
        UNIT=$?
        echo -e "\nfstrim -av"
        fstrim -av | grep "/qemu${UNIT}p" | sort -k5
        umount_image /dev/nbd$UNIT
        ;;
    esac
}


[ $# = 0 ] && help

if [ "$MYUNAME" != root ]
then
    echo -e "\033[33mSwitch root@$MYHNAME: sudo \"$0\" \"$@\"\033[0m"
    exec sudo "$0" "--chown=$(id -un):$(id -gn)" "$@"
fi

modprobe nbd max_part=8
[[ $1 =~ --chown=* ]] && OWNER=${1#*=} && shift
while [ $# != 0 ]
do
    case ${0##*/} in
    *trim*)
        trim_image "$1"
        ;;
    *umount*)
        umount_image "$1"
        ;;
    *)
        case ${1##*/} in
        *base*)
            mount_base_image "$1"
            ;;
        *)
            mount_image "$1"
            ;;
        esac
        ;;
    esac
    shift
done
