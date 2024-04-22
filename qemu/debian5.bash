#!/usr/bin/env bash
#
# Debian 5 x86 VM
#

qemu_settings() {
    MACHINE_TYPE=pc
    MACHINE_VCPUS=2
    MACHINE_RAM=2048
    DRIVE_INTERFACE=ide
    CONNECT_SSHPORT=2205
}


source ${0%/*}/qemu-system-x86_64.bash
