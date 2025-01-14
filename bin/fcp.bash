#!/usr/bin/env bash

set -u


#
# Function to parse options
#
options() {
    help() {
        echo "Usage: ${0%.bash} <options> source target"
        echo
        echo "Copy files and directories"
        echo
        echo "positional arguments:"
        echo "  source      Source file or directory."
        echo "  target      Target file or directory."
        exit $1
    }

    FLAGS="--recursive --links --perms --times --verbose --partial --progress"
    [ "$(rsync --help 2> /dev/null | grep info=)" ] && FLAGS="$FLAGS --info=progress2"
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
    case ${1:-} in
    --help)
      help 0
      ;;
    --*)
      help 1
      ;;
    esac
    [ $# -lt 2 ] && help 1
}

copy() {
    if [ -d "${@: -1}" ]
    then
        rsync $FLAGS "$@"/
    else
        rsync $FLAGS "$@"
    fi
}


options "$@"
copy "$@"
