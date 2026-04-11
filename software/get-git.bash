#!/usr/bin/env bash
#
# GIT 2.48.2 (Official) source code
#

set -e


source_settings() {
    NAME="git"
    VERSION="2.48.2"
    PORT="source-c"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://www.kernel.org/pub/software/scm/git/git-$VERSION.tar.xz
    "
    APP_SHELL="
        mv git-$VERSION/* .
        rm -rf git-$VERSION
        cp -p ${0%/*}/../compile/COMPILE-git.bash .
        touch -r README.md COMPILE-tmux.bash
    "
}


source "${0%/*}/setup-software.bash" source_settings
