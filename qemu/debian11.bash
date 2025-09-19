#!/usr/bin/env bash
#
# Debian 11 x86 VM
#

qemu_settings() {
    MACHINE_VCPUS=2
    MACHINE_RAM=2048
    CONNECT_NETWORK=no
    CONNECT_SOUND=yes
    CONNECT_SSHPORT=2211
}


source ${0%/*}/qemu-system-x86_64.bash
