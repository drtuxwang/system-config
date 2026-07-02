#!/usr/bin/env bash
#
# GIT 2.51.2 (Official) source code
#

set -e


source_settings() {
    NAME="git"
    VERSION="2.51.2"
    PORT="source-c"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://github.com/git/git/archive/refs/tags/v$VERSION.tar.gz
        ${0%/*}/../compile/COMPILE-git.bash
    "
    APP_SHELL="
        mv git-$VERSION/* .
        touch -r README.md COMPILE-tmux.bash
    "
    APP_REMOVE="
        git-$VERSION/
    "
}


source "${0%/*}/setup-software.bash" "$@" source_settings
