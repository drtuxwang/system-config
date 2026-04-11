#!/usr/bin/env bash
#
# TMUX 3.6a (Official) source code
#

set -e


source_settings() {
    NAME="tmux"
    VERSION="3.6a"
    PORT="source-c"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://github.com/tmux/tmux/releases/download/$VERSION/tmux-$VERSION.tar.gz
    "
    APP_SHELL="
        mv tmux-$VERSION/* .
        rm -rf tmux-$VERSION
        cp -p ${0%/*}/../compile/COMPILE-tmux.bash .
        touch -r CHANGES COMPILE-tmux.bash
    "
}


source "${0%/*}/setup-software.bash" source_settings
