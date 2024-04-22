#!/usr/bin/env bash
#
# Debian 12 x86 VM
#

qemu_settings() {
    MACHINE_VCPUS=2
    MACHINE_RAM=4096
    CONNECT_NETWORK=yes
    CONNECT_SOUND=yes
    CONNECT_SSHPORT=2212
}


source ${0%/*}/qemu-system-x86_64.bash
