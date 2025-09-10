#!/usr/bin/env bash
#
# $0 pre|post suspend|hibernate|hybrid-sleep
#

case $1 in
pre)
    ;;
post)
    killall pulseaudio
    ;;
esac
