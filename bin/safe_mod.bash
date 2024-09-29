#!/usr/bin/env bash
#
# Bash safe command module
#
# Copyright GPL v2: 2024 By Dr Colin Kong
#

set -u


#
# Run rm safely preventing unsafe rm arguments
#
safe_rm() {
    [ "$(echo " $* " | grep " / ")" ] && echo "rm: Unsafe to remove \"/\"" && exit 1
    [ "$(echo " $* " | grep " $(ls -1d /* 2> /dev/null | xargs echo) ")" ] && echo "rm: Unsafe to remove \"/*\"" && exit 1

    PATH=$(echo ":$PATH:" | sed -e "s@:${0%/*}:@:@;s/^://;s/:$//")
    exec "${0##*/}" "$@"
}

#
# Run rm safely preventing unsafe mv arguments
#
safe_mv() {
    [ "$(echo " $*" | grep " $(ls -1d /* 2> /dev/null | xargs echo) ")" ] && echo "mv: Unsafe to move \"/*\"" && exit 1

    PATH=$(echo ":$PATH:" | sed -e "s@:${0%/*}:@:@;s/^://;s/:$//")
    exec "${0##*/}" "$@"
}


safe_${0##*/} "$@"
