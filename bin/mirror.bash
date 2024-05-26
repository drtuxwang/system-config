#!/usr/bin/env bash

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
    REMOVE=
    case "${0##*/}" in
    *-rm)
        REMOVE="--delete-after"
        ;;
    esac
    while getopts "qhR" option
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
        rsync --archive --verbose --partial --progress $DELETE --info=progress2 "$SOURCE/" "$TARGET/"
    else
        rsync --filter="- ..fsum" --filter="- */" --archive --verbose --partial --progress $DELETE --info=progress2 "$SOURCE/" "$TARGET/"
    fi
}

options "$@"
mirror
