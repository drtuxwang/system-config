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
        cp -p -v "$TOPDIR"/config/profile rootfs/root/.profile
        cp -p -v "$TOPDIR"/config/bashrc rootfs/root/.bashrc
        ;;
    bash2ash)
        mkdir -p rootfs/bin
        cp -p -v "$TOPDIR"/docker/bin/bash2ash rootfs/bin/bash
        ;;
    bin)
        mkdir -p rootfs/opt/software/bin
        echo "'$TOPDIR/bin/*' -> 'rootfs/opt/software/*'"
        cp -p "$TOPDIR"/bin/* rootfs/opt/software/bin
        ;;
    bin-sysinfo)
        mkdir -p rootfs/opt/software/bin
        cp -p -v "$TOPDIR"/bin/sysinfo rootfs/opt/software/bin
        cp -p -v "$TOPDIR"/bin/sysinfo.sh rootfs/opt/software/bin
        ;;
    init)
        mkdir -p rootfs/etc
        cp -p -v files/docker-init rootfs/etc
        ;;
    python*)
        mkdir -p rootfs/etc
        VERSION=${1#python}
        for FILE in python-packages.bash python-requirements.txt python-requirements_$VERSION.txt
        do
            [ ! -f "$TOPDIR/etc/$FILE" ] && continue
            cp -p -v "$TOPDIR/etc/$FILE" rootfs/etc
        done
        ;;
    sudo)
        mkdir -p rootfs/etc/sudoers.d
        echo "Creating \"rootfs/etc/sudoers.d/allow-owner\"..."
        cp -p -v files/allow-owner rootfs/etc/sudoers.d
        ;;
    tmux)
        mkdir -p rootfs/root
        echo "Creating \"rootfs/root/.tmux.conf\"..."
        cp -p -v "$TOPDIR"/config/tmux.conf rootfs/root/.tmux.conf
        ;;
    vim)
        mkdir -p rootfs/root
        echo "Creating \"rootfs/root/.vimrc\"..."
        cp -p -v "$TOPDIR"/config/vimrc rootfs/root/.vimrc
        ;;
    xfce418)
        mkdir -p rootfs/home/owner/.config/autostart rootfs/home/owner/.config/xfce4/terminal rootfs/home/owner/.config/xfce4/xfconf/xfce-perchannel-xml rootfs/home/owner/.config/tigervnc
        echo "Creating \"rootfs/home/owner/.config\" XFCE setup..."
        cp -p -v files/xstartup rootfs/home/owner/.config/tigervnc
        cp -p -v "$TOPDIR"/config/autorun.desktop rootfs/home/owner/.config/autostart
        cp -p -v "$TOPDIR"/config/autorun-start.bash rootfs/home/owner/.config
        cp -p -v "$TOPDIR"/config/terminalrc-deb12 rootfs/home/owner/.config/xfce4/terminal/terminalrc
        cp -p -v "$TOPDIR"/config/thunar.xml-deb12 rootfs/home/owner/.config/xfce4/xfconf/xfce-perchannel-xml/thunar.xml
        cp -p -v "$TOPDIR"/config/xfce4-keyboard-shortcuts.xml-deb12 rootfs/home/owner/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml
        cp -p -v "$TOPDIR"/config/tmux.conf rootfs/home/owner/.config
        ;;
    xfce)
        mkdir -p rootfs/home/owner/.config/autostart rootfs/home/owner/.config/xfce4/xfconf/xfce-perchannel-xml rootfs/home/owner/.config/tigervnc
        echo "Creating \"rootfs/home/owner/.config/xfce4/terminal/terminalrc\"..."
        cp -p -v files/xstartup rootfs/home/owner/.config/tigervnc
        cp -p -v "$TOPDIR"/config/autorun.desktop rootfs/home/owner/.config/autostart
        cp -p -v "$TOPDIR"/config/autorun-start.bash rootfs/home/owner/.config
        cp -p -v "$TOPDIR"/config/thunar.xml rootfs/home/owner/.config/xfce4/xfconf/xfce-perchannel-xml/
		cp -p -v "$TOPDIR"/config/xfce4-keyboard-shortcuts.xml rootfs/home/owner/.config/xfce4/xfconf/xfce-perchannel-xml/
        cp -p -v "$TOPDIR"/config/xfce4-terminal.xml rootfs/home/owner/.config/xfce4/xfconf/xfce-perchannel-xml/
        cp -p -v "$TOPDIR"/config/tmux.conf rootfs/home/owner/.config
        ;;
    *)
        echo "$0: Unable to add \"$1\"."
        exit 1
    esac
    shift
done

# Fix file permissions
$TOPDIR/bin/fmod -R rootfs
