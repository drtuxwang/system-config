#!/usr/bin/env bash
#
# Git utilities module
#
# Copyright GPL v2: 2020-2025 By Dr Colin Kong
#

set -u


#
# Function to parse options
#
options() {
    help() {
        echo "Usage: $0 <options>"
        echo
        echo "git-diff   - Show git difference against origin default branch"
        echo "git-gc     - Run aggressive Git garbage collection"
        echo "git-reset  - Reset Git branch to origin/branch"
        echo "git-squash - Squash all commits in branch"
        echo
        echo "Options:"
        echo "  -h, --help  Show this help message and exit."
        echo "  <directory> Optional git directory."
        exit $1
    }

    case "${0##*/}" in
    *-diff|*-gc|*-reset|*-squash)
        mode=${0##*-}
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
    case ${1:-} in
    --help)
      help 0
      ;;
    --*)
      help 1
      ;;
    esac
}

#
# Function to show git difference against origin default branch
#
git_diff() {
    DEFAULT=$(git branch -r --list 'origin/HEAD' 2> /dev/null | awk '/ -> origin\// {print $NF}')
    git difftool --tool=meld --dir-diff $DEFAULT
}

#
# Function to run aggressive Git garbage collection"
#
git_gc() {
    DIR=$(git rev-parse --show-toplevel)
    du -s "$DIR"/.git
    rm -rf "$DIR"/.git/lfs
    git \
        -c gc.reflogExpire=0 \
        -c gc.reflogExpireUnreachable=0 \
        -c gc.rerereresolved=0 \
        -c gc.rerereunresolved=0 \
        -c gc.pruneExpire=now gc \
        --aggressive
    du -s "$DIR"/.git
}

#
# Function to reset Git branch to origin/branch"
#
git_reset() {
    git status
    git fetch --all --prune
    git reset --hard origin/`git rev-parse --abbrev-ref HEAD`
}

#
# Function to squash all commits in branch
#
git_squash() {
    git fetch origin
    DEFAULT=$(git rev-parse --abbrev-ref origin/HEAD | sed -e "s@.*/@@")
    git reset --soft $(git merge-base HEAD origin/$DEFAULT)
    git status
}


options "$@"

if [ $# = 0 ]
then
    git_$mode
else
    while [ $# != 0 ]
    do
        pushd "$1"
        git_$mode
        popd
        shift
    done
fi
