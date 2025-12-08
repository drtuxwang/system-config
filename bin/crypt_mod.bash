#!/usr/bin/env bash
#
# Bash encrypted partitions utilities module
#
# Copyright GPL v2: 2018-2025 By Dr Colin Kong
#

set -u

hostname=$(uname -n | tr '[A-Z]' '[a-z]' | cut -f1 -d".")
username=$(id -un)
mount_user=${SUDO_USER:-$username}


#
# Function to parse options
#
options() {
    help() {
        echo "Usage: $0 <options>"
        echo
        if [ "${0##*/}" = "crypt-format" ]
        then
            echo "crypt-format - Create LUKS encrypted partition and format"
            echo "Options:"
            echo "  -h, --help  Show this help message and exit."
            echo "  <device>    Select crypto_LUKS partition (ie sdc1)."
            echo "  <fstype>    Select f2fs or ext4."
            echo "  <volume>    Select partition volume name."
            exit $1
        fi

        echo "crypt-mount  - Mount LUKS encrypted partition"
        echo "crypt-umount - Unmmount LUKS encrypted partition"
        echo "crypt-format - Create LUKS encrypted partition and format"
        echo
        echo "Options:"
        echo "  -h, --help  Show this help message and exit."
        echo "  -a          Select all detected crypto_LUKS partitions."
        echo "  <device>    Select crypto_LUKS partition (ie sdc1)."
        echo "              Default select crypto_LUKS partitions on root drive."
        exit $1
    }

    uuids=
    case "${0##*/}" in
    *-format)
        mode=format
        [ $# != 3 ] && help 1
        [ "$2" != f2fs -a "$2" != ext4 ] && help 1
        return
        ;;
    *-mount)
        local rootdev=$(df / | awk '/^\/dev\// {print $1}' | sed -e "s@^/dev/@@;s/[0-9]*$//")
        uuids=$(lsblk -list -o NAME,FSTYPE,UUID 2> /dev/null | awk '/^'$rootdev'[1-9]* * crypto_LUKS/ {print $3}')
        mode=mount
        ;;
    *-umount)
        mode=unmount
        ;;
    *)
        help 0
        ;;
    esac
    while getopts "ah" option
    do
        case $option in
        a)
            uuids=$(lsblk -list -o NAME,FSTYPE,UUID 2> /dev/null | awk '/ crypto_LUKS/ {print $3}')
            ;;
        h)
            help 0
            ;;
        *)
            help 1
            ;;
        esac
    done
    shift $((OPTIND - 1))
    case ${1:-} in
    --help)
      help 0
      ;;
    --*)
      help 1
      ;;
    ?*)
        uuids=$(lsblk -list -o NAME,FSTYPE,UUID 2> /dev/null | awk '/^'"($(echo "$@" | sed -e "s@/@\/@g;s/ /|/g"))"' *crypto_LUKS/ {print $3; exit}' 2> /dev/null)
        ;;
    esac
}

#
# Function to become root user
#
become_root() {
    [ "$username" = root ] && return
    echo -e "\033[33mSwitch root@$hostname: sudo \"$0\"\033[0m"
    exec sudo "$0" $args_list
}

#
# Function to format encrypted partition
#
format_partition() {
    DEVICE="$1"
    local fstype="$2"
    local volume="$3"
    if [ "$fstype" = f2fs ]
    then
        echo "*** Format encrypted partition: mkfs.f2fs -l $volume /dev/mapper/$DEVICE"
        mkfs.f2fs -l $volume /dev/mapper/$DEVICE || return 1
    else
        echo "*** Format encrypted partition: mkfs.ext4 -L $volume /dev/mapper/$DEVICE"
        mkfs.ext4 -L $volume /dev/mapper/$DEVICE || return 1
        tune2fs -m 1 -c 256 -i 90d /dev/mapper/$DEVICE || return 1
    fi
    mkdir -p /media/$mount_user/$volume
    mount /dev/mapper/$DEVICE /media/$mount_user/$volume || return 1
    mkdir -p /media/$mount_user/$volume/$mount_user
    chown $mount_user:$(id -gn $mount_user) /media/$mount_user/$volume/$mount_user
    umount /media/$mount_user/$volume
}

#
# Function to create LUKS encrypted partition and format
#
format_crypt() {
    DEVICE="$1"
    echo
    echo "*** Creating LUKS encrypted partition: luksFormat /dev/$DEVICE"
    cryptsetup --cipher=aes-cbc-essiv:sha256 --key-size=256 --hash=sha256 --verify-passphrase \
        luksFormat /dev/$DEVICE || exit 1
    echo
    echo "*** Opening LUKS encrypted partition: luksOpen /dev/$DEVICE $DEVICE"
    cryptsetup --allow-discards --persistent luksOpen /dev/$DEVICE $DEVICE || exit 1:
    echo
    format_partition "$@"
    echo
    echo "*** Closing LUKS encrypted partition: luksClose /dev/mapper/$DEVICE"
    /sbin/cryptsetup luksClose /dev/mapper/$DEVICE
}

#
# Function to mount LUKS encrypted partition
#
mount_crypt() {
    local info=$(lsblk -list -o NAME,FSTYPE,UUID 2> /dev/null | awk '/crypto_LUKS .*'$1'/ {print $1, $3; exit}')
    local device="/dev/${info% *}"
    local uuid=${info#* }
    [ "$(lsblk -list -o NAME,MOUNTPOINT 2> /dev/null | awk '/^luks-'$uuid'/ {print $2}')" ] && return

    become_root
    echo -e "\033[33mLuksOpen on $hostname: UUID=$uuid ($device)\033[0m"
    /sbin/cryptsetup luksOpen UUID=$uuid luks-$uuid || exit 1
    local info=$(lsblk -list -o NAME,FSTYPE,LABEL 2> /dev/null | awk '/^luks-'$uuid'/ {print $2, $3}')
    local mount="/media/$mount_user/${info#* }"
    local fstype=${info% *}
    mkdir -p $mount
    chown $mount_user:$(id -gn $mount_user) ${mount%/*}

    case $fstype in
    f2fs)
        local options="-t f2fs -o lazytime,gc_merge,atgc"
        ;;
    ext4)
        local options="-t ext4 -o noatime,errors=remount-ro,commit=60"
        ;;
    vfat|ntfs)
        local options="mount -o uid=$mount_user,gid=$(id -gn $mount_user),umask=022,fmask=133"
        ;;
    *)
        local options=
        ;;
    esac
    echo "mount $options /dev/mapper/luks-$uuid $mount"
    mount $options /dev/mapper/luks-$uuid $mount

    [ "$(lsblk -list -o NAME,MOUNTPOINT | awk '/^luks-'$uuid'/ {print $2}')" ] && return
    echo "Error: Cannot find \"$hostname:$mount/$mount_user ($mount)\" failed..."
    exit 1
}

#
# Function to unmount LUKS encrypted partition
#
unmount_crypt() {
    local info=$(lsblk -list -o NAME,FSTYPE,UUID | awk '/crypto_LUKS '"$1"'/ {print $1, $3; exit}')
    local device="/dev/${info% *}"
    local uuid=${info#* }
    local mount=$(lsblk -list -o NAME,MOUNTPOINT | awk '/^luks-'$uuid'/ {print $2}')

    if [ "$mount" ]
    then
        become_root
        echo "Umounting on $hostname: /dev/mapper/luks-$uuid => $mount ($device)"
        umount $mount || exit 1
        rmdir $mount 2> /dev/null
    fi

    if [ -b /dev/mapper/luks-$uuid ]
    then
        become_root
        echo "LuksClose on $hostname: UUID=$uuid ($device)"
        /sbin/cryptsetup luksClose /dev/mapper/luks-$uuid
    fi
}

#
# Function to show mounted encrypted partitions
#
mount_info() {
    echo -e "\n$hostname:/dev/"
    lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT 2> /dev/null | grep -E "(luks-| crypto_LUKS )" | sed -e "s/..//"
    echo
}


options "$@"

args_list="$@"
[ "$mode" = format ] && ${mode}_crypt $args_list
for uuid in $uuids
do
    ${mode}_crypt $uuid
done
mount_info
