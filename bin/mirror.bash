#!/usr/bin/env bash

set -u


#
# Function to parse options
#
options() {
    help() {
        echo "Usage: ${0%.bash} <options> source_dir target_dir"
        echo
        echo "Copy all files/directory inside a directory into mirror directory."
        echo
        echo "Options:"
        echo "  -h, --help  Show this help message and exit."
        echo "  -R          Mirror directories recursively."
        echo "  -rm         Delete obsolete files in target directory."
        exit $1
    }

    RECURSIVE=
    FLAGS="--recursive --links --perms --times --verbose --partial --progress"
    [ "$(rsync --help 2> /dev/null | grep info=)" ] && FLAGS="$FLAGS --info=progress2"
    [ "${1:-}" = "-rm" ] && FLAGS="$FLAGS --delete-after" && shift
    while getopts "hR" option
    do
        case $option in
        h)
            help 0
            ;;
        R)
            RECURSIVE=1
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
    -rm)
      FLAGS="$FLAGS --delete-after"
      shift
      ;;
    --*)
      help 1
      ;;
    esac
    [ $# != 2 ] && help 1
    SOURCE="$1"
    TARGET="$2"
}


mirror() {
    if [ "$RECURSIVE" ]
    then
        rsync $FLAGS "$SOURCE/" "$TARGET/"
    else
        rsync --filter="- ..fsum" --filter="- */" $FLAGS "$SOURCE/" "$TARGET/"
    fi
}

options "$@"
mirror
