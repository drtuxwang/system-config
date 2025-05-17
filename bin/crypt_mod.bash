#!/usr/bin/env bash
#
# Bash encrypted partitions utilities module
#
# Copyright GPL v2: 2018-2024 By Dr Colin Kong
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
        echo "crypt-mount  - Mount LUKS encrypted partition"
        echo "crypt-umount - Unmmount LUKS encrypted partition"
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
for uuid in $uuids
do
    ${mode}_crypt $uuid
done
mount_info
