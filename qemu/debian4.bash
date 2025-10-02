#!/usr/bin/env bash
#
# Debian 4 x86 VM
#

qemu_settings() {
    MACHINE_TYPE=pc
    MACHINE_VCPUS=2
    MACHINE_RAM=2048
    DRIVE_INTERFACE=ide
    CONNECT_PASST_AUTO=no
    CONNECT_SSHPORT=2204
}


source ${0%/*}/qemu-system-x86_64.bash
