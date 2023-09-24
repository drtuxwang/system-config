#!/usr/bin/env bash
#
# qemu-img create -f qcow2 debian8.vm.vda.qcow2 8M  # Boot disk
# qemu-img create -f qcow2 debian8.vm.vdb.qcow2 2048M
#

qemu_settings() {
    MACHINE_VCPUS=2
    MACHINE_RAM=2048
    CONNECT_SSHPORT=2208
}


source ${0%/*}/qemu-system-x86_64.bash
