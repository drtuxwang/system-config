#!/usr/bin/env bash
#
# QEMU VM start script
#
# Host (192.168.56.2):
#   ssh -p <port> localhost
#   scp -P <port> localhost:/path .
# Guest: (Ctrl-Alt+G)
#   mount -t 9p -o uid=owner,gid=users,msize=131072 Shared /mnt/host &
# Images:
#   qemu-img create -f qcow2 name.boot.qcow2 8M
#   qemu-img create -f qcow2 name_root.qcow2.snap 8192M
#   qemu-img create -F qcow2 -b file.qcow2.snap -f qcow2 file.qcow2
#   qemu-img convert -p -f vdi file1.vdi -O qcow2 file2.qcow2
#   qemu-img convert -p -f qcow2 file1.qcow2 -O qcow2 -c -o compression_type=zstd file2.qcow2
#

defaults_settings() {
    COMMAND="qemu-system-x86_64"
    FILE=${0##*/}
    MACHINE_NAME=${FILE%.*}
    MACHINE_ACCEL=yes
    MACHINE_TYPE=q35
    MACHINE_VCPUS=2
    MACHINE_RAM=4096
    MACHINE_BIOS=
    DRIVE_INTERFACE=virtio
    DRIVE_FILES=
    DRIVE_TMPDIR="/tmp/qemu-$(id -un)"
    CONNECT_DISPLAY=yes
    CONNECT_NETWORK=no
    CONNECT_PASST_AUTO=yes
    CONNECT_SSHPORT=
    CONNECT_SHARE=$(realpath "$HOME/Desktop/shared")
    CONNECT_SOUND=no
    VERBOSE=no
    DRYRUN=no
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
    echo "Debug: DRIVE_TMPDIR=$DRIVE_TMPDIR"
    echo "Debug: CONNECT_DISPLAY=$CONNECT_DISPLAY"
    echo "Debug: CONNECT_NETWORK=$CONNECT_NETWORK"
    echo "Debug: CONNECT_PASST_AUTO=$CONNECT_PASST_AUTO"
    echo "Debug: CONNECT_SOUND=$CONNECT_SOUND"
    echo "Debug: CONNECT_SSHPORT=$CONNECT_SSHPORT"
    echo "Debug: CONNECT_SHARE=$CONNECT_SHARE"
    echo "Debug: VERBOSE=$VERBOSE"
    echo "Debug: DRYRUN=$DRYRUN"
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
            echo "  -net        Connect VM to network"
            echo "  -nonet      Disable network (internet)"
            echo "  -novirt     Disable virtualisation (use full emulation)"
            echo "  -x          Enable GUI display"
            echo "  -nox        Disable GUI display"
            echo "  -v          Show debug info"
            echo "  -test       Show debug info without starting QEMU"
            echo "  file.qcow2  Attach disk image file"
            echo "  file.iso    Attach CD/DVD iso file"
            exit 0
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
        -x)
            CONNECT_DISPLAY=yes
            ;;
        -nox)
            CONNECT_DISPLAY=no
            ;;
        -v)
            VERBOSE=yes
            ;;
        -test)
            VERBOSE=yes
            DRYRUN=yes
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
    DRIVE_FILES="$(ls -1 ${0%/*}/${MACHINE_NAME}/*qcow2* 2> /dev/null | awk '{printf("%s ", $1)}')$DRIVE_FILES"
}

snapshot_drive() {
   [ "$(ls -1t "$(realpath $1)" "$2" 2> /dev/null | head -1)" = "$2" ] && return
   echo -e "\nqemu-img create -F qcow2 -b $(realpath $1) -f qcow2 $2"
   qemu-img create -F qcow2 -b $(realpath $1) -f qcow2 $2
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
    CPU="qemu64 -smp $MACHINE_VCPUS"
    if [ "$MACHINE_ACCEL" = yes ]
    then
        case $(uname -a) in
        Darwin*x86_64*)
            MACHINE_TYPE="$MACHINE_TYPE -accel hvf"
            CPU="host,-pdpe1gb -smp $MACHINE_VCPUS"
            ;;
        Linux*x86_64*)
            MACHINE_TYPE="$MACHINE_TYPE -accel kvm"
            CPU="host -smp $MACHINE_VCPUS"
            ;;
        esac
    fi
    add_args "-machine $MACHINE_TYPE" "-cpu $CPU" "-m $MACHINE_RAM"
    [ "$MACHINE_BIOS" ] && add_args "-bios $MACHINE_BIOS"
    add_args "-boot order=dc -no-fd-bootchk"
}

setup_drives() {
    mkdir -p "$DRIVE_TMPDIR/$MACHINE_NAME" && chmod go= "$DRIVE_TMPDIR"
    for FILE in $DRIVE_FILES
    do
        MOUNT_DEV="$FILE"
        MOUNT_OPT="if=$DRIVE_INTERFACE,discard=unmap"
        case ${FILE##*/} in
        *.iso)
            MOUNT_OPT="if=ide,media=cdrom"
            ;;
        *qcow2.snap*)
            MOUNT_DEV="${FILE%.snap*}"
            snapshot_drive $FILE $MOUNT_DEV
        esac
        add_args "-drive file=$MOUNT_DEV,$MOUNT_OPT" || continue
        [ "$VERBOSE" = yes ] && echo -e "\nqemu-img info $MOUNT_DEV" && qemu-img info $MOUNT_DEV
    done
}

setup_connects() {
    add_args "-serial none" "-parallel none"
    add_args "-usb -device usb-tablet -device usb-kbd"
    [ "$CONNECT_SOUND" = yes ] && add_args "-device intel-hda -device hda-output"
    [ "$CONNECT_DISPLAY" != yes ] && add_args "-display none"
    SLIRP="-nic user,ipv4=on,net=192.168.56.0/24"
    [ "$CONNECT_SSHPORT" ] && SLIRP="$SLIRP,hostfwd=tcp::$CONNECT_SSHPORT-:22"
    OFFLINE=yes
    if [ "$CONNECT_NETWORK" = yes ]
    then
        PASST=
        [ "$CONNECT_PASST_AUTO" = yes ] && PASST=$(umask 077; passt --one-off 2>&1 | awk '/UNIX.*socket bound at / {print $NF; exit}')
        if [ "$PASST" ]
        then
            add_args "-device virtio-net-pci,netdev=s"
            add_args "-netdev stream,id=s,server=off,addr.type=unix,addr.path=$PASST"
        else
            OFFLINE=no  # SLIRP external network fallback
        fi
    fi
    add_args "$SLIRP,restrict=$OFFLINE" && \
    [ -d "$CONNECT_SHARE" ] && add_args "-virtfs local,path=$CONNECT_SHARE,mount_tag=Shared,multidevs=remap,security_model=none"
}

setup() {
    defaults_settings
    [[ $(type -t qemu_settings) == function ]] && qemu_settings
    parse_options "$@"
    [ "$VERBOSE" = yes ] && show_settings

    setup_machine
    setup_drives
    setup_connects
}


setup "$@"
echo
echo "$COMMAND" | sed -e 's/$/ \\/;$s/ \\//'
[ "$DRYRUN" = yes ] && exit

trap true INT
($COMMAND 2>&1 | grep -Ev ": warning: dbind:| pw.conf "; rm -rf "$DRIVE_TMPDIR/$MACHINE_NAME") &
[ "$CONNECT_DISPLAY" != yes ] && wait
