#!/usr/bin/env bash
#
# TMUX 3.6b (Official) source code
#

set -e


source_settings() {
    NAME="tmux"
    VERSION="3.6b"
    PORT="source-c"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://github.com/tmux/tmux/releases/download/$VERSION/tmux-$VERSION.tar.gz
        ${0%/*}/../compile/COMPILE-tmux.bash
    "
    APP_SHELL="
        mv tmux-$VERSION/* .
        touch -r CHANGES COMPILE-tmux.bash
    "
    APP_REMOVE="
        tmux-$VERSION/
    "
}


source "${0%/*}/setup-software.bash" "$@" source_settings
