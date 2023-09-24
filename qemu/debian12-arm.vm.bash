#!/usr/bin/env bash
#
# qemu-img create -f qcow2 debian12-arm.vm.vda.qcow2 8M  # Boot disk
# qemu-img create -f qcow2 debian12-arm.vm.vdb.qcow2 2048M
#

qemu_settings() {
    MACHINE_VCPUS=2
    MACHINE_RAM=4096
    CONNECT_SSHPORT=2222
}


source ${0%/*}/qemu-system-aarch64.bash
