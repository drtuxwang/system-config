#!/usr/bin/env bash
#
# qemu-img convert -p file.vdi -O qcow2 -c -o compression_type=zstd windows7-32.vm.vda-base.qcow2
# qemu-img create -F qcow2 -b windows7-32.vm.vda-base.qcow2 -f qcow2 windows7-32.vm.vda.qcow2  # Also rollback
#

qemu_settings() {
    MACHINE_TYPE=pc
    MACHINE_VCPUS=2
    MACHINE_RAM=4096
    DRIVE_INTERFACE=ide
}


source ${0%/*}/qemu-system-x86_64.bash
