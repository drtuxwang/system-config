#!/usr/bin/env bash
#
# Windows 10 x86 VM
#

qemu_settings() {
    MACHINE_TYPE=pc
    MACHINE_VCPUS=2
    MACHINE_RAM=4096
    DRIVE_INTERFACE=ide
}


source ${0%/*}/qemu-system-x86_64.bash
