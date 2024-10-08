#!/usr/bin/env bash
#
# Bash host connection utilities module
#
# Copyright GPL v2: 2021-2024 By Dr Colin Kong
#

set -u

TIMEOUT="timeout -s KILL 10"


#
# Function to parse options
#
options() {
    help() {
        echo "Usage: $0 <options> <host> [<host> ...] [-- <cmdline>]"
        echo
        echo "host-run    - Run command on remote hosts"
        echo "host-keys   - Add SSH private key for hosts to authentication agent"
        echo "host-setup  - Setup remote hosts"
        echo "host-mount  - Mount remote host file system"
        echo "host-umount - Unmount remote host file system"
        echo
        echo "Options:"
        echo "  -h, --help  Show this help message and exit."
        echo "  host        Host name."
        echo "  cmdline     Command line and arguments."
        exit $1
    }

    smount_dir="${TMPDIR:-/tmp/$(id -un)}/hosts"
    case "${0##*/}" in
    *-run|*-keys|*-setup|*-mount|*-umount)
        mode=${0##*-}
        ;;
    ssh|scp)
        mode="${0##*/}"
        return
        ;;
    *)
        help 0
        ;;
    esac
    while getopts "h" option
    do
        case $option in
        h)
            help 0
            ;;
        *)
            help 1
            ;;
        esac
    done
    shift $((OPTIND - 1))
    hosts=
    while [ $# != 0 ]
    do
        case ${1:-} in
        --help)
            help 0
            ;;
        --)
            break
            ;;
        --*)
            help 1
            ;;
        [a-zA-Z]*)
            hosts="$hosts$1 "
            shift
            ;;
        *)
            help 1
            ;;
        esac
    done
}

#
# Function to show local hosts
#
show_local() {
    avahi-browse --all --terminate 2> /dev/null | grep Workstation | awk '{printf("%s:%s %s.%s %s\n", $2, $3, $4, $7, $5)}' | sort
}

#
# Function to run command on remote hosts
#
run_host() {
    [ ! "$hosts" ] && show_local && return

    while [ $# != 0 ]
    do
       if [ "$1" = "--" ]
       then
           shift
           for host in $hosts
           do
               OUTPUT=$(ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no $host "$@" 2>&1)
               echo "$OUTPUT" | grep -Ev "^(Warning: Permanently added|YOU HAVE CONNECTED|$)" | sed -e "s/^/$host: /"
           done
           return
      fi
      shift
   done
}

#
# Function to add SSH private key for hosts to authentication agent
#
keys_host() {
    for host in $*
    do
        for key in $(ssh -G "$host" 2> /dev/null | awk '/^identityfile / {print $2}' | sed -e "s@\~@$HOME@")
        do
            if [ -f "$key" ]
            then
                id=$(awk '{print $3}' "$key.pub" 2> /dev/null)
                if [ ! "$(ssh-add -l 2> /dev/null | grep -E " ($key|$id) ")" -a "$SSH_AUTH_SOCK" ]
                then
                    echo -e "\033[33mSSH key for $host: ssh-add $key\033[0m"
                    ssh-add $key
                fi
                break
            fi
        done
    done
    ssh-add -l
}

#
# Function to setup remote hosts
#
setup_host() {
    [ ! "$hosts" ] && show_local && return

    sysinfo=$(which sysinfo)
    for host in $hosts
    do
        echo "$host: setup"
        $TIMEOUT ssh -o BatchMode=yes -o StrictHostKeyChecking=no $host exit 2>&1 | grep "Permission denied" && ssh-copy-id $host
        $TIMEOUT ssh $host rm -f .bash_logout .bash_profile .emacs 2> /dev/null || continue
        $TIMEOUT scp -p $HOME/.profile $HOME/.profile-opt $HOME/.vimrc $host: 2> /dev/null || continue
        [ "$($TIMEOUT ssh $host test -x /opt/software/bin/sysinfo.sh 2> /dev/null)" ] && continue
        $TIMEOUT ssh $host mkdir -p software/bin 2> /dev/null || continue
        $TIMEOUT scp -p $sysinfo $sysinfo.sh $host:software/bin 2> /dev/null || continue
        echo "$host: ok"
    done
}

#
# Function to fix host mounts by removing broken sshfs mounts
#
fix_mounts() {
    for remdir in $smount_dir/*
    do
        timeout -s KILL 2 ls $remdir/etc > /dev/null 2>&1 || fusermount -uz $remdir 2> /dev/null
    done
    rmdir $smount_dir/* 2> /dev/null
}

#
# Function to show host mounts
#
show_mounts() {
    mount | grep "$smount_dir"
}

#
# Function to mount remote host file system
#
mount_host() {
    fix_mounts
    [ ! "$hosts" ] && show_mounts && return

    for host in $hosts
    do
        remdir="$smount_dir/$(echo $host | tr '[A-Z]' '[a-z]' | cut -f1 -d".")"
        if [ ! "$(mount | grep " $remdir ")" ]
        then
            mkdir -p $remdir 2> /dev/null
            smount $host:/ $remdir
        fi
        mount | grep " $remdir "
    done
}

#
# Function to unmount remote host file system
#
unmount_host() {
    fix_mounts
    [ ! "$hosts" ] && show_mounts && return

    for host in $hosts
    do
        remdir="$smount_dir/$(echo $host | tr '[A-Z]' '[a-z]' | cut -f1 -d".")"
        sumount $remdir
    done
}

#
# Run ssh with auto ssh-add keys
#
ssh_host() {
    if  [ -e "$SSH_AUTH_SOCK" ]
    then
        case ${1:-} in
        -*)
            ;;
        [a-z]*)
            ssh_add ${1%%.*}
            ;;
        esac
    fi

    PATH=$(echo ":$PATH:" | sed -e "s@:${0%/*}:@:@;s/^://;s/:$//")
    exec "${0##*/}" "$@"
}

#
# Run scp with auto ssh-add keys
#
scp_host() {
    if  [ -e "$SSH_AUTH_SOCK" ]
    then
        for ARG in $*
        do
            case $ARG in
            [a-z]*:*)
                 ssh_add ${ARG%%:*}
                 ;;
            esac
        done
    fi

    PATH=$(echo ":$PATH:" | sed -e "s@:${0%/*}:@:@;s/^://;s/:$//")
    exec "${0##*/}" "$@"
}

#
# Function to add ssh keys
#
ssh_add() {
    for _host in $*
    do
        for _key in $(ssh -G "$_host" 2> /dev/null | awk '/^identityfile / {print $2}' | sed -e "s@\~@$HOME@")
        do
            if [ -f "$_key" ]
            then
                _id=$(awk '{print $3}' "$_key.pub" 2> /dev/null)
                if [ ! "$(ssh-add -l 2> /dev/null | grep -E " ($_key|$_id) ")" -a "$SSH_AUTH_SOCK" ]
                then
                    echo -e "\033[33mSSH key for $_host: ssh-add $_key\033[0m"
                    ssh-add $_key
                fi
                break
           fi
       done
   done
}


options "$@"

${mode}_host "$@"
