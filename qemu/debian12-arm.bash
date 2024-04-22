#!/usr/bin/env bash
#
# Debian 12 arm64 VM
#

qemu_settings() {
    MACHINE_VCPUS=2
    MACHINE_RAM=4096
    CONNECT_SOUND=yes
    CONNECT_SSHPORT=2292
}


source ${0%/*}/qemu-system-aarch64.bash
