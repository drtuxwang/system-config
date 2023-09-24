#!/usr/bin/env bash
#
# QEMU VM start script
#
# Host:
#   ssh -p <port> localhost
#   scp -P <port> localhost:/path .
# Guest: (Ctrl-Alt+G)
#   mount -t 9p -o uid=owner,gid=users,msize=131072 Shared /mnt/host &
#   ssh 192.168.56.2
# Images:
#   qemu-img create -f qcow2 name.vda.qcow2 8M
#   qemu-img create -f qcow2 name.vdb.qcow2 8192M
#   qemu-img create -F qcow2 -b name.vdb-base.qcow2 -f qcow2 name.vdb.qcow2
#   qemu-img convert -f vdi file1.vdi -O qcow2 file2.qcow2
#   qemu-img convert -f qcow2 file1.qcow2 -O qcow2 -c -o compression_type=zstd file2.qcow2
#

defaults_settings() {
    COMMAND="qemu-system-aarch64"
    FILE=${0##*/}
    MACHINE_NAME=${FILE%.*}
    MACHINE_ACCEL=yes
    MACHINE_TYPE=virt
    MACHINE_VCPUS=2
    MACHINE_RAM=4096
    MACHINE_BIOS="/usr/share/qemu-efi-aarch64/QEMU_EFI.fd"
    DRIVE_INTERFACE=virtio
    DRIVE_FILES=
    DRIVE_ROLLBACK=no
    DRIVE_SNAPSHOT=no
    DRIVE_TMPDIR=${TMPDIR:-/tmp/$(id -un)}/qemu
    CONNECT_DISPLAY=yes
    CONNECT_NETWORK=no
    CONNECT_SSHPORT=
    CONNECT_SHARE=$(realpath "$HOME/Desktop/shared")
    DEBUG=no

    [ $(uname) = Darwin ] && BIOS="/usr/local/Cellar/qemu/$(qemu-system-aarch64 --version | awk '/^QEMU emulator / {print $NF}')/share/qemu/edk2-aarch64-code.fd"
}

show_settings() {
    echo
    echo "Debug: COMMAND=$COMMAND"
    echo "Debug: MACHINE_NAME=$MACHINE_NAME"
    echo "Debug: MACHINE_ACCEL=$MACHINE_ACCEL"
    echo "Debug: MACHINE_TYPE=$MACHINE_TYPE"
    echo "Debug: MACHINE_VCPUS=$MACHINE_VCPUS"
    echo "Debug: MACHINE_RAM=$MACHINE_RAM"
    echo "Debug: MACHINE_BIOS=$MACHINE_BIOS"
    echo "Debug: DRIVE_INTERFACE=$DRIVE_INTERFACE"
    echo "Debug: DRIVE_FILES=$DRIVE_FILES"
    echo "Debug: DRIVE_ROLLBACK=$DRIVE_ROLLBACK"
    echo "Debug: DRIVE_SNAPSHOT=$DRIVE_SNAPSHOT"
    echo "Debug: DRIVE_TMPDIR=$DRIVE_TMPDIR"
    echo "Debug: CONNECT_DISPLAY=$CONNECT_DISPLAY"
    echo "Debug: CONNECT_NETWORK=$CONNECT_NETWORK"
    echo "Debug: CONNECT_SSHPORT=$CONNECT_SSHPORT"
    echo "Debug: CONNECT_SHARE=$CONNECT_SHARE"
    echo "Debug: DEBUG=$DEBUG"
}

parse_options() {
    while [ $# != 0 ]
    do
        case $1 in
        -h|-help|--help)
            echo "Usage: $0 <options>"
            echo
            echo "Options:"
            echo "  -h, --help  Show this help message and exit"
            echo "  -debug      Show debug info without starting QEMU"
            echo "  -net        Connect VM to network"
            echo "  -nonet      Disable network (internet)"
            echo "  -novirt     Disable virtualisation (use full emulation)"
            echo "  -nox        Disable GUI display"
            echo "  -rollback   Rollback drives to base snapshot"
            echo "  -snap       Snapshot drives and auto rollback after execution"
            echo "  file.qcow2  Attach disk image file"
            echo "  file.iso    Attach CD/DVD iso file"
            exit 0
            ;;
        -debug)
            DEBUG=yes
            ;;
        -net)
            CONNECT_NETWORK=yes
            ;;
        -nonet)
            CONNECT_NETWORK=no
            ;;
        -novirt)
            MACHINE_ACCEL=no
           ;;
        -nox)
            CONNECT_DISPLAY=no
            ;;
        -rollback)
            DRIVE_ROLLBACK=yes
            ;;
        -snap)
            DRIVE_SNAPSHOT=yes
            ;;
        *.qcow2|*.iso)
            DRIVE_FILES="$DRIVE_FILES$(realpath "$1") "
            ;;
        *)
            echo "$0: error: unrecognized arguments: $1"
            exit 1
            ;;
         esac
         shift
    done
}

snapshot_drive() {
   [ ! -f "$2" ] && retrun
   echo -e "\nqemu-img create -F qcow2 -b $(realpath $1) -f qcow2 $2"
   qemu-img create -F qcow2 -b $(realpath $1) -f qcow2 $2
}


rollback_drives() {
    for FILE in $(ls -1 ${0%/*}/$MACHINE_NAME.vd[a-z]-base.qcow2 2> /dev/null | sed -e "s/-base.qcow2$/.qcow2/")
    do
        rm -f $FILE
        snapshot_drive $BASE ${BASE//-base/}
    done
}

add_args() {
    while [ $# != 0 ]
    do
        [ "$(echo "$COMMAND" | grep "^    $1$")" ] && return 1
        COMMAND="$COMMAND
    $1"
        shift
    done
}

setup_machine() {
    add_args "-name $MACHINE_NAME"
    CPU="max -smp $MACHINE_VCPUS"
    if [ "$MACHINE_ACCEL" = yes ]
    then
        case $(uname -a) in
        Darwin*arm64*)
            MACHINE_TYPE="$MACHINE_TYPE -accel hvf"
            CPU="host"
            ;;
        Linux*arm64*)
            MACHINE_TYPE="$MACHINE_TYPE -accel kvm"
            CPU="host"
            ;;
        esac
    fi
    add_args "-machine $MACHINE_TYPE" "-cpu $CPU -smp $MACHINE_VCPUS" "-m $MACHINE_RAM"
    [ "$MACHINE_BIOS" ] && add_args "-bios $MACHINE_BIOS"
    add_args "-boot order=dc"
}

setup_drives() {
    for BASE in $(ls -1 ${0%/*}/$MACHINE_NAME.vd[a-z]-base.qcow2 2> /dev/null)
    do
        snapshot_drive $BASE ${BASE//-base/}
    done
    [ "$DRIVE_ROLLBACK" = yes ] && rollback_drives

    DRIVE_FILES="$(ls -1 ${0%/*}/$MACHINE_NAME.vd[a-z].qcow2 2> /dev/null | awk '{printf("%s ", $1)}') $DRIVE_FILES"
    mkdir -p "$DRIVE_TMPDIR/$MACHINE_NAME" && chmod go= "$DRIVE_TMPDIR"
    for FILE in $DRIVE_FILES
    do
        MOUNT_DEV=$(realpath "$FILE")
        MOUNT_OPT="if=$DRIVE_INTERFACE,discard=unmap"
        case ${FILE##*/} in
        *.iso)
            MOUNT_OPT="if=$DRIVE_INTERFACE,media=cdrom"
            ;;
        *base*)
            MOUNT_DEV="$DRIVE_TMPDIR/${FILE##*/}"
            snapshot_drive $FILE $MOUNT_DEV
            ;;
        *)
            if [ "$DRIVE_SNAPSHOT" = yes ]
            then
                MOUNT_DEV="$DRIVE_TMPDIR/$MACHINE_NAME/${FILE##*/}"
                snapshot_drive $FILE $MOUNT_DEV
            fi
            ;;
        esac
        add_args "-drive file=$MOUNT_DEV,$MOUNT_OPT" || continue
        echo -e "\nqemu-img info $MOUNT_DEV"
        qemu-img info $MOUNT_DEV
    done
}

setup_connects() {
    [ "$CONNECT_DISPLAY" != yes ] && add_args "-display none"
    NETWORK="user,net=192.168.56.0/24"
    [ "$CONNECT_SSHPORT" ] && NETWORK="$NETWORK,hostfwd=tcp::$CONNECT_SSHPORT-:22"
    [ "$CONNECT_NETWORK" != yes ] && NETWORK="$NETWORK,restrict=yes"
    add_args "-nic $NETWORK"
    [ -d "$CONNECT_SHARE" ] && add_args "-virtfs local,path=$CONNECT_SHARE,mount_tag=Shared,multidevs=remap,security_model=none"
}

setup() {
    defaults_settings
    [[ $(type -t qemu_settings) == function ]] && qemu_settings
    parse_options "$@"
    [ "$DEBUG" = yes ] && show_settings

    setup_machine
    setup_drives
    setup_connects
}


setup "$@"
echo
echo "$COMMAND" | sed -e 's/$/ \\/;$s/ \\//'
[ "$DEBUG" = yes ] && exit

trap true INT
($COMMAND 2>&1 | grep -v ": warning: dbind:"; rm -rf "$DRIVE_TMPDIR/$MACHINE_NAME") &
[ "$CONNECT_DISPLAY" != yes ] && wait
