#!/usr/bin/env bash
#
# Debian 12 x86 VM
#

qemu_settings() {
    MACHINE_VCPUS=4
    MACHINE_RAM=8192
    CONNECT_NETWORK=yes
    CONNECT_SOUND=yes
    CONNECT_SSHPORT=2212
}


source ${0%/*}/qemu-system-x86_64.bash
