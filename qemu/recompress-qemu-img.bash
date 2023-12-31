#!/usr/bin/env bash

set -u

while [ $# -gt 0 ]
do
    case "$1" in
    *.qcow2)
        echo "qemu-img convert -f qcow2 \"$1\" -O qcow2 -c -o compression_type=zstd \"$1-new\""
        qemu-img convert -f qcow2 "$1" -O qcow2 -c -o compression_type=zstd "$1-new"
        ;;
    esac
    shift
done
