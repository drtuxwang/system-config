#!/usr/bin/env bash

set -eu

if [ $# = 0 ]
then
    echo "Usage: $0 select1 [select2 [...]]"
    exit 1
fi

TOPDIR=$(realpath "$0" | sed -e "s|/[^/]*/[^/]*/[^/]*$||")
umask 022
rm -rf rootfs

while [ "$#" != 0 ]
do
    case "$1" in
    bash)
        mkdir -p rootfs/root
        echo "Creating \"rootfs/root/.profile\"..."
        cp -p "$TOPDIR"/config/profile rootfs/root/.profile
        echo "Creating \"rootfs/root/.bashrc\"..."
        cp -p "$TOPDIR"/config/bashrc rootfs/root/.bashrc
        ;;
    bash2ash)
        mkdir -p rootfs/bin
        echo "Creating \"rootfs/bin/bash\"..."
        cp -p "$TOPDIR"/docker/bin/bash2ash rootfs/bin/bash
        ;;
    bin)
        mkdir -p rootfs/opt/software/bin
        echo "Creating \"rootfs/opt/software/bin/*\"..."
        cp -p "$TOPDIR"/bin/[A-Za-z0-9]* rootfs/opt/software/bin
        ;;
    bin-sysinfo)
        mkdir -p rootfs/opt/software/bin
        echo "Creating \"rootfs/opt/software/bin/sysinfo\"..."
        cp -p "$TOPDIR"/bin/sysinfo rootfs/opt/software/bin
        echo "Creating \"rootfs/opt/software/bin/sysinfo.sh\"..."
        cp -p "$TOPDIR"/bin/sysinfo.sh rootfs/opt/software/bin
        ;;
    init)
        mkdir -p rootfs/etc
        echo "Creating \"rootfs/etc/docker-init\"..."
        cp -p files/docker-init rootfs/etc
        ;;
    python*)
        mkdir -p rootfs/etc
        VERSION=${1#python}
        for FILE in python-packages.sh python-requirements.txt python-requirements_$VERSION.txt
        do
            [ ! -f "$TOPDIR/etc/$FILE" ] && continue
            echo "Creating \"rootfs/etc/$FILE\"..."
            cp -p "$TOPDIR/etc/$FILE" rootfs/etc
        done
        ;;
    sudo)
        echo "Creating \"rootfs/etc/sudoers.d/allow-owner\"..."
        mkdir -p rootfs/etc/sudoers.d
        cp -p files/allow-owner rootfs/etc/sudoers.d
        ;;
    tmux)
        echo "Creating \"rootfs/root/.tmux.conf\"..."
        mkdir -p rootfs/root
        cp -p "$TOPDIR"/config/tmux.conf rootfs/root/.tmux.conf
        ;;
    vim)
        echo "Creating \"rootfs/root/.vimrc\"..."
        mkdir -p rootfs/root
        cp -p "$TOPDIR"/config/vimrc rootfs/root/.vimrc
        ;;
    xfce)
        mkdir -p rootfs/.config/xfce4/terminal rootfs/.vnc
        echo "Creating \"rootfs/.config/xfce4/terminal/terminalrc\"..."
        cp -p "$TOPDIR"/config/terminalrc rootfs/.config/xfce4/terminal
        if [ -f "files/xstartup" ]
        then
            echo "Creating \"rootfs/.vnc/xstartup\"..."
            cp -p files/xstartup rootfs/.vnc
        fi
        ;;
    *)
        echo "$0: Unable to add \"$1\"."
        exit 1
    esac
    shift
done

# Fix file permissions
$TOPDIR/bin/fmod -R rootfs
