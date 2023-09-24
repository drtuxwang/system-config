#!/usr/bin/env bash
#
# qemu-img convert file.vdi -O qcow2 -c -o compression_type=zstd windowsxp-32.vm.vda-base.qcow2
# qemu-img create -F qcow2 -b windowsxp-32.vm.vda-base.qcow2 -f qcow2 windowsxp-32.vm.vda.qcow2  # Also rollback
#

qemu_settings() {
    MACHINE_TYPE=pc
    DRIVE_INTERFACE=ide
    MACHINE_VCPUS=2
    MACHINE_RAM=2048
}


source ${0%/*}/qemu-system-x86_64.bash
