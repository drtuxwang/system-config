#!/usr/bin/env bash
#
# qemu-img create -f qcow2 debian11.vm.vda.qcow2 8M  # Boot disk
# qemu-img create -f qcow2 debian11.vm.vdb.qcow2 10G
#

qemu_settings() {
    MACHINE_VCPUS=2
    MACHINE_RAM=4096
    CONNECT_NETWORK=yes
    CONNECT_SSHPORT=2211
}


source ${0%/*}/qemu-system-x86_64.bash
