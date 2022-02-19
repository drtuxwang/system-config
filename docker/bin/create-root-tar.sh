#!/usr/bin/env bash

set -eu

if [ $# = 0 ]
then
    echo "Usage: $0 select1 [select2 [...]]"
    exit 1
fi

TOPDIR=$(realpath "$0" | sed -e "s|/[^/]*/[^/]*/[^/]*$||")
umask 022
rm -rf tmpdir/root

while [ "$#" != 0 ]
do
    case "$1" in
    bash)
        mkdir -p tmpdir/root-disk/root
        echo "Creating \"tmpdir/root-disk/root/.profile\"..."
        cp -p "$TOPDIR"/config/profile tmpdir/root-disk/root/.profile
        echo "Creating \"tmpdir/root-disk/root/.bashrc\"..."
        ln -sf .profile tmpdir/root-disk/root/.bashrc
        ;;
    bash2ash)
        mkdir -p tmpdir/root-disk/bin
        echo "Creating \"tmpdir/root-disk/bin/bash\"..."
        cp -p "$TOPDIR"/docker/bin/bash2ash tmpdir/root-disk/bin/bash
        ;;
    bin)
        mkdir -p tmpdir/root-disk/opt/software/bin
        echo "Creating \"tmpdir/root-disk/opt/software/bin/*\"..."
        cp -p "$TOPDIR"/bin/* tmpdir/root-disk/opt/software/bin
        ;;
    bin-sysinfo)
        mkdir -p tmpdir/root-disk/opt/software/bin
        echo "Creating \"tmpdir/root-disk/opt/software/bin/sysinfo\"..."
        cp -p "$TOPDIR"/bin/sysinfo tmpdir/root-disk/opt/software/bin
        echo "Creating \"tmpdir/root-disk/opt/software/bin/sysinfo.sh\"..."
        cp -p "$TOPDIR"/bin/sysinfo.sh tmpdir/root-disk/opt/software/bin
        ;;
    init)
        mkdir -p tmpdir/root-disk/etc
        echo "Creating \"tmpdir/root-disk/etc/docker-init\"..."
        cp -p files/docker-init tmpdir/root-disk/etc
        ;;
    sudo)
        echo "Creating \"tmpdir/root-disk/etc/sudoers.d/allow-owner\"..."
        mkdir -p tmpdir/root-disk/etc/sudoers.d
        cp -p files/allow-owner tmpdir/root-disk/etc/sudoers.d
        ;;
    tmux)
        echo "Creating \"tmpdir/root-disk/root/.tmux.conf\"..."
        mkdir -p tmpdir/root-disk/root
        cp -p "$TOPDIR"/config/tmux.conf tmpdir/root-disk/root/.tmux.conf
        ;;
    vim)
        echo "Creating \"tmpdir/root-disk/root/.vimrc\"..."
        mkdir -p tmpdir/root-disk/root
        cp -p "$TOPDIR"/config/vimrc tmpdir/root-disk/root/.vimrc
        ;;
    xfce)
        mkdir -p tmpdir/root-disk/.config/xfce4/terminal tmpdir/root-disk/.vnc
        echo "Creating \"tmpdir/root-disk/.config/xfce4/terminal/terminalrc\"..."
        cp -p "$TOPDIR"/config/terminalrc tmpdir/root-disk/.config/xfce4/terminal
        if [ -f "files/xstartup" ]
        then
            echo "Creating \"tmpdir/root-disk/.vnc/xstartup\"..."
            cp -p files/xstartup tmpdir/root-disk/.vnc
        fi
        ;;
    *)
        echo "$0: Unable to add \"$1\"."
        exit 1
    esac
    shift
done

# Fix group and others file/directory read access recursively
for FILE in $(find tmpdir -type f)
do
    if [ -x "$FILE" ]
    then
        chmod 755 $FILE
    else
        chmod 644 $FILE
    fi
done
[[ -d tmpdir/root-disk/.ssh ]] && chmod 700 tmpdir/root-disk/.ssh

if [ -d tmpdir/root-disk ]
then
    pushd tmpdir/root-disk > /dev/null
    echo "Creating \"tmpdir/root.tar\"..."
    tar cf ../root.tar * --owner=0:0 --group=0:0
    popd > /dev/null
fi
