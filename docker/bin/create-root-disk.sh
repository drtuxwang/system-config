#!/usr/bin/env bash

set -eu

if [ $# = 0 ]
then
    echo "Usage: $0 select1 [select2 [...]]"
    exit 1
fi

TOPDIR=$(realpath "$0" | sed -e "s|/[^/]*/[^/]*/[^/]*$||")
umask 022
rm -rf root-disk

while [ "$#" != 0 ]
do
    case "$1" in
    bash)
        mkdir -p root-disk/root
        echo "Creating \"root-disk/root/.profile\"..."
        cp -p "$TOPDIR"/config/profile root-disk/root/.profile
        echo "Creating \"root-disk/root/.bashrc\"..."
        ln -sf .profile root-disk/root/.bashrc
        ;;
    bash2ash)
        mkdir -p root-disk/bin
        echo "Creating \"root-disk/bin/bash\"..."
        cp -p "$TOPDIR"/docker/bin/bash2ash root-disk/bin/bash
        ;;
    bin)
        mkdir -p root-disk/opt/software/bin
        echo "Creating \"root-disk/opt/software/bin/*\"..."
        cp -p "$TOPDIR"/bin/* root-disk/opt/software/bin
        ;;
    bin-sysinfo)
        mkdir -p root-disk/opt/software/bin
        echo "Creating \"root-disk/opt/software/bin/sysinfo\"..."
        cp -p "$TOPDIR"/bin/sysinfo root-disk/opt/software/bin
        echo "Creating \"root-disk/opt/software/bin/sysinfo.sh\"..."
        cp -p "$TOPDIR"/bin/sysinfo.sh root-disk/opt/software/bin
        ;;
    init)
        mkdir -p root-disk/etc
        echo "Creating \"root-disk/etc/docker-init\"..."
        cp -p files/docker-init root-disk/etc
        ;;
    python*)
        mkdir -p root-disk/etc
        echo "Creating \"root-disk/etc/python-packages.sh\"..."
        cp -p "$TOPDIR"/etc/python-packages.sh root-disk/etc
        echo "Creating \"root-disk/etc/python-requirements.txt\"..."
        cp -p "$TOPDIR"/etc/python-requirements.txt root-disk/etc
        VERSION=${1#python}
        if [ "$VERSION" -a -f "$TOPDIR"/etc/python$VERSION-requirements.txt ]
        then
            echo "Creating \"root-disk/etc/python$VERSION-requirements.txt\"..."
            cp -p "$TOPDIR"/etc/python$VERSION-requirements.txt root-disk/etc
        fi
        ;;
    sudo)
        echo "Creating \"root-disk/etc/sudoers.d/allow-owner\"..."
        mkdir -p root-disk/etc/sudoers.d
        cp -p files/allow-owner root-disk/etc/sudoers.d
        ;;
    tmux)
        echo "Creating \"root-disk/root/.tmux.conf\"..."
        mkdir -p root-disk/root
        cp -p "$TOPDIR"/config/tmux.conf root-disk/root/.tmux.conf
        ;;
    vim)
        echo "Creating \"root-disk/root/.vimrc\"..."
        mkdir -p root-disk/root
        cp -p "$TOPDIR"/config/vimrc root-disk/root/.vimrc
        ;;
    xfce)
        mkdir -p root-disk/.config/xfce4/terminal root-disk/.vnc
        echo "Creating \"root-disk/.config/xfce4/terminal/terminalrc\"..."
        cp -p "$TOPDIR"/config/terminalrc root-disk/.config/xfce4/terminal
        if [ -f "files/xstartup" ]
        then
            echo "Creating \"root-disk/.vnc/xstartup\"..."
            cp -p files/xstartup root-disk/.vnc
        fi
        ;;
    *)
        echo "$0: Unable to add \"$1\"."
        exit 1
    esac
    shift
done

# Fix file permissions
$TOPDIR/bin/fmod -R root-disk
