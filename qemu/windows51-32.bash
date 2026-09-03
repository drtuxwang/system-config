#!/usr/bin/env bash
#
# Windows XP x86 VM
#

qemu_settings() {
    MACHINE_TYPE=pc
    DRIVE_INTERFACE=ide
    MACHINE_VCPUS=2
    MACHINE_RAM=4096
}


source ${0%/*}/qemu-system-x86_64.bash
