#!/usr/bin/env bash
#
# qemu-img create -f qcow2 debian4.vm.vda.qcow2 8M  # Boot disk
# qemu-img create -f qcow2 debian4.vm.vdb.qcow2 1536M
#

qemu_settings() {
    MACHINE_TYPE=pc
    MACHINE_VCPUS=2
    MACHINE_RAM=2048
    DRIVE_INTERFACE=ide
    CONNECT_SSHPORT=2204
}


source ${0%/*}/qemu-system-x86_64.bash
