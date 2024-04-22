#!/usr/bin/env bash
#
# Debian 6 x86 VM
#

qemu_settings() {
    MACHINE_VCPUS=2
    MACHINE_RAM=2048
    CONNECT_SSHPORT=2206
}


source ${0%/*}/qemu-system-x86_64.bash
