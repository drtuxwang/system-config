#!/usr/bin/env bash
#
# qemu-img create -f qcow2 debianmac.vm.vda.qcow2 8M  # Boot disk
# qemu-img create -f qcow2 debianmac.vm.vdb.qcow2 16G
# qemu-img create -f qcow2 debianmac.vm.vdc.qcow2 128G
#

qemu_settings() {
    MACHINE_VCPUS=2
    MACHINE_RAM=4096
    CONNECT_NETWORK=yes
    CONNECT_SOUND=yes
    CONNECT_SSHPORT=2212
}


source ${0%/*}/qemu-system-x86_64.bash
