#!/usr/bin/env bash
#
# Debian 10 x86 VM
#

qemu_settings() {
    MACHINE_VCPUS=2
    MACHINE_RAM=4096
    CONNECT_SSHPORT=2291
}


source ${0%/*}/qemu-system-x86_64.bash
