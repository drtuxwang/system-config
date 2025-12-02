#!/bin/sh
#
# System configuration detection tool
#
# 1996-2025 By Dr Colin Kong
#
VERSION=20251202
RELEASE="2.6.57"

# Test for bash echo bug
if [ "`echo \"\n\"`" = "\n" ]
then
    ECHO="echo -e"
else
    ECHO=echo
fi

# Workaround GNU Textutil POSIX 200112 bug
if [ "`(echo | head -1 | tail +1) 2>&1`" ]
then
    _POSIX2_VERSION=199209
    export _POSIX2_VERSION
fi

# Avoid GNU egrep usage
if [ "`grep --version 2> /dev/null | grep 'GNU grep'`" ]
then
    egrep () {
        grep -E "$@"
        return $?
    }
fi

# Avoids Bash cd PATH problems
unset CDPATH

# HP-UX ps fix
if [ "`uname`" = HP-UX ]
then
    UNIX95=a
fi


#
# Function to return location of program
#
which() {
    if [ "$1" = "`basename $0`" ]
    then
        PATH=`echo ":$PATH:" | sed -e "s@:\`dirname \"$0\"\`:@:@;s/^://;s/:$//"`
    fi
    for CDIR in `echo $PATH | sed -e "s/ /%20/g" -e "s/:/ /g"`
    do
        CMD=`echo "$CDIR/$1" | sed -e "s/%20/ /g"`
        if [ -x "$CMD" -a ! -d "$CMD" ]
        then
            echo "$CMD" | sed -e "s@//*@/@g"
            return
        fi
    done
}

#
# Set to Unknown if not set
#
isitset() {
    if [ $# = 0 -o "$1" = 0 ]
    then
        echo Unknown
    else
        echo "$@"
    fi
}

#
# Write info if found
#
write_found() {
    if [ ! "`echo \" $@ \" | grep \" value= \"`" ]
    then
        if [ "`echo \" $@ \" | egrep \" (location|value)=[^ ]\"`" ]
        then
            write_output "$@"
        fi
    fi
}

#
# Function to scan system bus (Linux only)
#
scanbus() {
    LSUSB=`PATH=/sbin:$PATH lsusb 2> /dev/null`

    # Audio device detection
    for CARD in `egrep "^ ?[0-9][0-9]* " /proc/asound/cards | awk '{print $1}'`
    do
        UNIT=`echo $CARD | sed -e "s/^0$//"`
        if [ "`ls /proc/asound/card$CARD/midi* 2> /dev/null`" ]
        then
            MODEL=`grep "^ $CARD " /proc/asound/cards 2> /dev/null | sed -e "s/^[^:]*: //"`
            write_output name="Audio device" device="/dev/midi$UNIT" value="$MODEL" comment="MIDI"
        fi
        for FILE in `ls -1 /proc/asound/card$CARD/pcm*[cp]/info`
        do
            NAME="`grep \" $CARD \" /proc/asound/cards | sed -e "s/.*- //"` `grep \"^name: \" $FILE | sed -e "s/name: //"`"
            DEVICE="/dev/snd/pcmC${CARD}D`echo $FILE | sed -e "s@.*pcm@@;s@/.*@@"`"
            if [ -e $DEVICE ]
            then
                case $FILE in
                */pcm*p/*)
                    write_output name="Audio device" device="$DEVICE" value="$NAME" comment="SPK"
                    ;;
                *)
                    write_output name="Audio device" device="$DEVICE" value="$NAME" comment="MIC"
                    ;;
                esac
            fi
        done
    done

    # Battery detection
    for BATTERY in `ls -1d /proc/acpi/battery/BAT* 2> /dev/null`
    do
        INFO=`cat $BATTERY/info $BATTERY/state 2> /dev/null`
        if [ "`echo \"$INFO\" | grep \"present:.*yes\"`" ]
        then
            BATOEM=`echo "$INFO" | grep "^OEM info:" | sed -e "s/.*: *//"`
            BATNAME=`echo "$INFO" | grep "^model number:" | sed -e "s/.*: *//"`
            BATTYPE=`echo "$INFO" | grep "^battery type:" | sed -e "s/.*: *//"`
            BATCAP=`echo "$INFO" | grep "^design capacity:" | sed -e "s/.*: *//" -e "s/ //g"`
            BATVOLT=`echo "$INFO" | grep "^design voltage:" | sed -e "s/.*: *//" -e "s/ //g"`
            MYCAP=`echo "$INFO" | grep "^remaining capacity:" | sed -e "s/.*: *//" -e "s/ //g"`
            MYRATE=`echo "$INFO" | grep "^present rate:" | sed -e "s/.*: *//" | awk '{print $1}'`
            if [ "`echo \"$INFO\" | grep \"charging state:.*discharging\"`" ]
            then
                if [ "$MYRATE" = unknown ]
                then
                    STATE="-"
                else
                    STATE="-"`echo "$MYRATE" "$MYCAP" | awk '{printf("%dmA, %3.1fh\n", $1, $2/$1)}'`
                fi
            elif [ "`echo \"$INFO\" | grep \"charging state:.*charging\"`" ]
            then
                if [ "$MYRATE" = unknown ]
                then
                    STATE="+"
                else
                    STATE="+"`echo "$MYRATE" | awk '{printf("%dmA\n",$1)}'`
                fi
            else
                STATE="="
            fi
            write_output name="Battery device" device="/dev/???" value="$MYCAP" comment="$BATOEM $BATNAME $BATTYPE $BATCAP/$BATVOLT [$STATE]"
        fi
    done

    # CD device detection
    for DEVICE in `ls /proc/ide 2> /dev/null`
    do
        if [ "`grep ide-cdrom /proc/ide/$DEVICE/driver 2> /dev/null`" ]
        then
            MODEL=`sed -e "s/CDRW/CD-RW/" -e "s@ RW/D@ CD-RW/D@" /proc/ide/$DEVICE/model`
            write_output name="CD device" device="/dev/$DEVICE" value="$MODEL"
        fi
    done
    SCSI=`tail +2 /proc/scsi/scsi 2> /dev/null | paste - - - | grep "CD-ROM" |
    sed -e "s/^Host: scsi//" -e "s/Vendor://" -e "s/Model://" -e "s/Rev:.*//" -e "s/CDRW/CD-RW/" -e "s@ RW/D@ CD-RW/D@" | awk '{printf(" %d,%d,%d,%d %s %s %s %s %s\n", $1, $3, $5, $7, $8, $9, $10, $11, $12)}'`
    for UNIT in `echo "$SCSI" | awk '{print $1}'`
    do
        MODEL=`echo "$SCSI" | grep " $UNIT " | cut -f3- -d" "`
        DEVICE=`ls -ld /sys/block/sr*/device 2> /dev/null | grep "/\`echo $UNIT | sed -e \"s/,/:/g\"\`$" | cut -f4 -d/`
        if [ ! "$DEVICE" ]
        then
            DEVICE=sr`expr \`echo "$SCSI" | grep -n $UNIT | cut -f1 -d:\` - 1`
        fi
        if [ -b /dev/`echo $DEVICE | sed -e "s/sr/scd/"` ]
        then
            DEVICE=`echo $DEVICE | sed -e "s/sr/scd/"`
        fi
        if [ -f /proc/scsi/usb-storage*/`echo $UNIT | cut -f1 -d","` ]
        then
            MODEL="$MODEL [USB]"
        elif [ -f /proc/scsi/ide-scsi*/`echo $UNIT | cut -f1 -d","` ]
        then
            MODEL="$MODEL [IDE]"
        fi
        write_output name="CD device" device="/dev/$DEVICE" value="$MODEL"
    done

    # Disk IDE device detection
    for DEVICE in `ls /proc/ide 2> /dev/null`
    do
        if [ "`grep ide-disk /proc/ide/$DEVICE/driver 2> /dev/null`" ]
        then
            MODEL=`cat /proc/ide/$DEVICE/model`
            for PART in `grep " $DEVICE" /proc/partitions 2> /dev/null | awk '{print $4}'`
            do
                SIZE=`egrep " $PART( |$)" /proc/partitions | awk '{print $3}'`
                case $PART in
                *[1-9]*)
                    if [ "`grep \"/dev/$PART \" /proc/swaps 2> /dev/null`" ]
                    then
                        write_output name="Disk device" device="/dev/$PART" value="$SIZE KB" comment="swap"
                    else
                        write_output name="Disk device" device="/dev/$PART" value="$SIZE KB" comment="`mount 2> /dev/null | grep \"/dev/$PART \" | awk '{printf(\"%s on %s\",$5,$3)}'`"
                    fi
                    ;;
                *)
                    write_output name="Disk device" device="/dev/$PART" value="$SIZE KB" comment="`echo $SIZE | awk '{printf(\"%dGB '\"$MODEL\"'\",$1*1024/1000000000)}'`"
                    ;;
                esac
            done
        fi
    done

    # Disk SCSI device detection ("/sys/bus/scsi/devices" new method)
    if [ -d "/sys/bus/scsi/devices" ]
    then
        for DIR in /sys/block/*d[a-z]*/device
        do
            IDENTITY=`ls -ld "$DIR" | sed -e "s@.*/@@"`
            if [ "$IDENTITY" ]
            then
                MODEL=`sed -e "s/ *//g" /sys/bus/scsi/devices/$IDENTITY/vendor /sys/bus/scsi/devices/$IDENTITY/model | paste - - -d" "`
                SDX=`basename \`dirname $DIR\``
                SIZE=`grep " $SDX" /proc/partitions | head -1 | awk '{print $3}'`
                MOUNT=`grep "^/dev/$SDX " /proc/mounts | awk '{print $2}'`
                if [ "$MOUNT" ]
                then
                    TYPE=`grep "^/dev/$SDX " /proc/mounts | awk '{print $3}'`
                    write_output name="Disk device" device="/dev/$SDX" value="$SIZE KB" comment="$TYPE on $MOUNT, $MODEL"
                else
                    write_output name="Disk device" device="/dev/$SDX" value="$SIZE KB" comment="$MODEL"
                fi
                for SDXN in `grep " $SDX[1-9]" /proc/partitions | awk '{print $NF}'`
                do
                    SIZE=`grep " $SDXN$" /proc/partitions | head -1 | awk '{print $3}'`
                    MOUNT=`grep "^/dev/$SDXN " /proc/mounts | awk '{print $2}'`
                    if [ "$MOUNT" ]
                    then
                        TYPE=`grep "^/dev/$SDXN " /proc/mounts | awk '{print $3}'`
                        write_output name="Disk device" device="/dev/$SDXN" value="$SIZE KB" comment="$TYPE on $MOUNT"
                    elif [ "`ls /sys/class/block/dm-*/slaves/$SDXN 2> /dev/null`" ]
                    then
                        write_output name="Disk device" device="/dev/$SDXN" value="$SIZE KB" comment="devicemapper"
                    else
                        write_output name="Disk device" device="/dev/$SDXN" value="$SIZE KB"
                    fi
                done
            fi
        done

    # Disk SCSI device detection ("/proc/scsi/scsi" old method)
    else
        SCSI=`tail +2 /proc/scsi/scsi 2> /dev/null | paste - - - | grep "Direct-Access" | sed -e "s/^Host: scsi//" -e "s/Vendor://" -e "s/Model://" -e "s/Rev:.*//" | awk '{printf (" %d,%d,%d,%d %s %s %s %s %s \n", $1, $3, $5, $7, $8, $9, $10, $11, $12)}' | sed -e "s/ *$//"`
        for UNIT in `echo "$SCSI" | awk '{print $1}'`
        do
            MODEL=`echo "$SCSI" | grep " $UNIT " | cut -f3- -d" "`
            DEVICE=`ls -ld /sys/block/sd*/device 2> /dev/null | grep "/\`echo $UNIT | sed -e \"s/,/:/g\"\`$" | cut -f4 -d/`
            if [ ! "$DEVICE" ]
            then
                DEVICE=sd`echo -e "\14\`echo "$SCSI" | grep -n $UNIT | cut -f1 -d:\`"`
            fi
            if [ -f /proc/scsi/usb-storage*/`echo $UNIT | cut -f1 -d","` ]
            then
                if [ "`grep \"Attached: No\" /proc/scsi/usb-storage*/\`echo $UNIT | cut -f1 -d\",\"\``" ]
                then
                    continue
                fi
                MODEL="$MODEL [USB]"
            fi
            for PART in `grep " $DEVICE" /proc/partitions 2> /dev/null | awk '{print $NF}'`
            do
                SIZE=`grep " $PART$" /proc/partitions | awk '{print $3}'`
                case $PART in
                *[1-9]*)
                    if [ "`grep \"/dev/$PART \" /proc/swaps 2> /dev/null`" ]
                    then
                        write_output name="Disk device" device="/dev/$PART" value="$SIZE KB" comment="swap"
                    else
                        for MOUNT in `mount 2> /dev/null | grep "/dev/$PART " | awk '{printf("%s,%s\n",$5,$3)}'`
                        do
                            write_output name="Disk device" device="/dev/$PART" value="$SIZE KB" comment="`echo \"$MOUNT\" | sed -e \"s/,/ on /\"`"
                        done
                    fi
                    ;;
                *)
                    write_output name="Disk device" device="/dev/$PART" value="$SIZE KB" comment="`echo $SIZE | awk '{printf(\"%dGB '\"$MODEL\"'\",$1*1024/1000000000)}'`"
                    ;;
                esac
            done
        done
    fi

    # Disk mapper detection
    MOUNTS=`grep "/dev/mapper/" /proc/mounts | sort`
    TIMEOUT=`timeout --version 2> /dev/null | grep "^timeout " | sed -e "s/^timeout.*/timeout 1s/"`
    for DIR in /sys/class/block/dm-*
    do
        if [ -f "$DIR/dm/name" ]
        then
            DEVICE="/dev/mapper/`cat \"$DIR/dm/name\"`"
            SIZE=`cat "$DIR/size" | awk '{print $1/2}'`
            SLAVES=`cut -f1 -d"-" $DIR/dm/uuid`:`ls -1 $DIR/slaves | awk '{printf("%s+", $1)}' | sed -e "s/+$//"`
            if [ "`grep ^/dev/\`basename $DIR\` /proc/swaps`" ]
            then
                write_output name="Disk device" device="$DEVICE" value="$SIZE KB" comment="swap, $SLAVES"
            else
                for MOUNT in `echo "$MOUNTS" | grep "^$DEVICE " | awk '{print $2}'`
                do
                    TYPE=`echo "$MOUNTS" | grep " $MOUNT " | awk '{print $3}'`
                    write_output name="Disk device" device="$DEVICE" value="$SIZE KB" comment="$TYPE on $MOUNT, $SLAVES"
                done
            fi
        fi
    done

    # Disk remote detection
    MOUNTS=`grep ":" /proc/mounts | awk '{printf("%s %s %s\n", $1, $3, $2)}' | sort`
    TIMEOUT=`timeout --version 2> /dev/null | grep "^timeout " | sed -e "s/^timeout.*/timeout 1s/"`
    for MOUNT in `echo "$MOUNTS" | awk '{print $3}'`
    do
        DEVICE=`echo "$MOUNTS" | grep " $MOUNT$" | awk '{print $1}'`
        TYPE=`echo "$MOUNTS" | grep " $MOUNT$" | awk '{print $2}'`
        SIZE=`$TIMEOUT df -k $MOUNT 2> /dev/null | tail +2 | paste - - | awk '{print $2}'`
        if [ ! "$SIZE" -o "$SIZE" = 0 ]
        then
            SIZE="???"
        fi
        write_output name="Disk device" device="$DEVICE" value="$SIZE KB" comment="$TYPE on $MOUNT"
    done

    # Graphics device detection
    if [ -d "/dev/dri" ]
    then
        GPUS=`ls -1d /sys/bus/pci/devices/*/drm/card* 2> /dev/null`
    else
        GPUS=`ls -1d /sys/bus/pci/devices/*/graphics/fb* 2> /dev/null`
    fi
    if [ "$GPUS" ]
    then
        for GPU in $GPUS
        do
            if [ -d "/dev/dri" ]
            then
                DEVICE=/dev/dri/`basename $GPU`
            else
                DEVICE=/dev/`basename $GPU`
            fi
            if [ -e "$DEVICE" ]
            then
                MODEL=`echo "$LSPCI" | grep "^\`echo \"$GPU\" | sed -e \"s@.*/[^:]*:@@;s@/.*@@\"\` " | sed -e "s/.*controller: //"`
                write_output name="Graphics device" device="$DEVICE" value="$MODEL"
            fi
        done
    else
        if [ "`xrandr 2> /dev/null`" ]
        then
            MODELS=`echo "$LSPCI" | grep "VGA compatible controller:" | sed -e "s/.*controller: //" -e "s/ /#/g"`
            for MODEL in $MODELS
            do
                write_output name="Graphics device" device="/dev/???" value="`echo \"$MODEL\" | sed -e \"s/\#/ /g\"`"
            done
        fi
    fi

    # Input device detection
    INPUTS=`egrep "^(N|H):"  /proc/bus/input/devices 2> /dev/null | paste - -`
    EVENTS=`ls -l /dev/input/by-path/* 2> /dev/null | grep "/event" | sed -e "s@.*/@@"`
    for EVENT in $EVENTS
    do
        MODEL=`echo "$INPUTS" | grep "$EVENT " | cut -f2 -d'"'`
        write_output name="Input device" device="/dev/input/$EVENT" value="$MODEL"
    done

    # Network device detection
    for NETWORK in `ls -1d /sys/bus/pci/devices/*/net/* /sys/bus/pci/devices/*/net:* 2> /dev/null | sed -e "s@net:@net/@"`
    do
        MODEL=`echo "$LSPCI" | grep "^\`echo "$NETWORK" | sed -e \"s@.*/[^:]*:@@;s@/.*@@\"\` " | sed -e "s/.*controller: //"`
        MODEL=`echo "$LSPCI" | grep "^\`echo "$NETWORK" | sed -e \"s@.*/[^:]*:@@;s@/.*@@\"\` " | sed -e "s/.*: //;s/Semiconductor//;s/Co., //;s/Ltd. //;s/PCI Express //"`
        write_output name="Network device" device="net/`basename $NETWORK`" value="`isitset $MODEL`"
    done

    # Video device detection
    for DEVICE in `ls -1 /sys/class/video4linux 2> /dev/null`
    do
        if [ "`grep \"^DEVTYPE=usb_\" /sys/class/video4linux/$DEVICE/device/uevent 2> /dev/null`" ]
        then
            MODEL=`echo "$LSUSB" | grep "\`grep DEVICE= /sys/class/video4linux/$DEVICE/device/uevent | sed -e \"s@/@ @g\" | awk '{printf(\"Bus %s Device %s:\n\",$5,$6)}'\`" | sed -e "s/.*: ID [^ ]* //"`" [USB]"
        elif [ -f /sys/class/video4linux/$DEVICE/model ]
        then
            MODEL=`cat /sys/class/video4linux/$DEVICE/model 2> /dev/null | sed -e "s/ *$/)/"`
        else
            MODEL="???"
        fi
        if [ "$MODEL" ]
        then
            write_output name="Video device" device="/dev/$DEVICE" value="$MODEL"
        fi
    done
}

#
# Function to detect configurations
#
detect() {
    if [ ! "$SHORT" ]
    then
        AUTHOR="Sysinfo $RELEASE (`echo $VERSION | cut -c1-4`-`echo $VERSION | cut -c5-6`-`echo $VERSION | cut -c7-8`)"
        TIME=`date +'%Y-%m-%d-%H:%M:%S'`
        $ECHO "$AUTHOR - System configuration detection tool"
        $ECHO "\n*** Detected at $TIME ***"
    fi

    if [ "$SHORT" = net -o ! "$SHORT" ]
    then
        # Detect host information
        MYHNAME=`uname -n | tr '[A-Z]' '[a-z]' | cut -f1 -d"."`
        case `uname` in
        AIX)
            INETS=`isitset \`/usr/sbin/ifconfig -a 2> /dev/null | grep "inet[6]* " | sed -e "s/inet[6]*/ /" | awk '{print $1}'\``
            ;;
        Darwin)
            INETS=`/sbin/ifconfig -a 2> /dev/null | grep "inet6* " | awk '{print $2}' | cut -f1 -d% | uniq`
            ;;
        HP-UX)
            INETS=`isitset \`(/usr/sbin/ifconfig lan0; /usr/sbin/ifconfig lan1; /usr/sbin/ifconfig lan2) 2> /dev/null | grep "inet[6]* " | sed -e "s/inet[6]*/ /" | awk '{print $1}'\``
            ;;
        IRIX*)
            INETS=`isitset \`/usr/etc/ifconfig -a 2> /dev/null | grep "inet[6]* " | sed -e "s/inet[6]*/ /" | awk '{print $1}'\``
            if [ "$INETS" = Unknown ]
            then
                INETS=`/usr/etc/ping -c 1 $MYHNAME 2>&1 | grep "([.0-9]*)" | head -1 | cut -f2 -d"(" | cut -f1 -d")"`
            fi
            ;;
        Linux)
            if [ -x "/bin/ip" ]
            then
                INETS=`/bin/ip address 2> /dev/null | grep "^ *inet[6]* " | awk '{print $2}'`
            else
                INETS=`LANG=en_GB isitset \`/sbin/ifconfig -a 2> /dev/null | grep "^ *inet6* " | sed -e "s/ addr[a-z]*://;s/inet[6]*/ /" | awk '{print $1}' | uniq\``
            fi
            ;;
        *NT*)
            INETS=`isitset \`$WINDIR/system32/ipconfig 2> /dev/null | grep "IP.* Address" | sed -e "s/.*: //"\``
        ;;
        OSF1|SunOS|*)
            INETS=`isitset \`/sbin/ifconfig -a 2> /dev/null | grep "inet[6]* " | sed -e "s/inet[6]*/ /" | awk '{print $1}'\``
            ;;
        esac

        write_output name="Hostname" value="$MYHNAME"
        for INET in $INETS
        do
            write_output name="INET Address" value="$INET"
        done
        for HOST in `grep "^[     ]*nameserver[     ]*[1-9]" /etc/resolv.conf 2> /dev/null | awk '{print $2}'`
        do
            write_output name="INET Nameserver" value="$HOST"
        done
        write_found name="INET IPv4 Public" value="`curl --ipv4 --connect-timeout 1 http://ifconfig.me 2> /dev/null`"
        write_found name="INET IPv6 Public" value="`curl --ipv6 --connect-timeout 1 http://ifconfig.me 2> /dev/null`"
        write_found name="INET Dflt Public" value="`curl --connect-timeout 1 http://ifconfig.me 2> /dev/null`"
    fi

    # Detect hardware information
    MYTYPE=Unknown
    MYCPUS=Unknown
    MYBIT=Unknown
    MYCLOCK=Unknown
    MYCACHE=Unknown
    MYRAM=Unknown
    MYSWAP=Unknown
    MYOSNAME=Unknown
    MYOSKERNEL=Unknown
    MYOSPATCH=Unknown
    MYOSBOOT=Unknown
    MYTYPEX=
    MYCPUSX=
    MYBITSX=
    MYCACHEX=
    MYRAMX=
    MYSWAPX=
    case `uname` in
    AIX)
        MYOSTYPE="aix"
        MYOSNAME="AIX $(oslevel)`oslevel -s 2>&1 | head -1 | grep \"^....-\" | sed -e "s/5380-00/5300-08/" -e \"s/^[^-]*-/-/\"`"
        ;;
    IRIX*)
        MYOSTYPE="irix"
        if [ "`/bin/uname -R | sed -e 's/.* //' | grep \"^[1-9]\"`" ]
        then
            MYOSNAME="IRIX `/bin/uname -R | sed -e 's/.* //'`"
        else
            MYOSNAME="IRIX `/bin/uname -r`"
        fi
        ;;

    Linux)
        MYOSTYPE="linux"
        MYOSNAME=
        if [ "`dpkg --list 2> /dev/null | grep \"ii  mepis-auto\"`" ]
        then
            MYOSNAME="MEPIS "`dpkg --list | grep "ii  mepis-auto" | head -1 | awk '{print $3}'`
        elif [ "`grep \"^DISTRIB_DESCRIPTION=\" /etc/lsb-release 2> /dev/null`" ]
        then
            MYOSNAME=`grep "^DISTRIB_DESCRIPTION=" /etc/lsb-release | cut -f2 -d"=" | sed -e "s/\"//g"`
        elif [ "`egrep \"^DISTRIB_ID=|^DISTRIB_RELEASE=\" /etc/lsb-release 2> /dev/null | wc -l | awk '{print $1}'`" = 2 ]
        then
            MYOSNAME="`grep \"^DISTRIB_ID=\" /etc/lsb-release | cut -f2 -d\"=\"` `grep \"^DISTRIB_RELEASE=\" /etc/lsb-release | cut -f2 -d\"=\"`"
        elif [ -f /etc/kanotix-version ]
        then
            MYOSNAME="Kanotix `awk '{print $2}' /etc/kanotix-version`"
        elif [ -f /etc/knoppix-version ]
        then
            MYOSNAME="Knoppix `awk '{print $1}' /etc/knoppix-version`"
        elif [ -f /etc/DISTRO_SPECS ]
        then
            MYOSNAME="`grep ^DISTRO_NAME /etc/DISTRO_SPECS | cut -f2 -d= | sed -e \"s/\'//g\"` `grep ^DISTRO_VERSION /etc/DISTRO_SPECS | cut -f2 -d=`"
        elif [ -f /etc/alpine-release ]
        then
            MYOSNAME="Alpine `cat /etc/alpine-release`"
        elif [ "`dpkg --list 2> /dev/null | grep \"ii  knoppix\"`" ]
        then
            MYOSNAME="Knoppix "`dpkg --list | grep "ii  knoppix-g" | awk '{print $3}' | sed -e "s/-.*//"`
        elif [ "`dpkg --list 2> /dev/null | grep \"ii  kernel.*MEPIS\"`" ]
        then
            MYOSNAME="MEPIS "`dpkg --list | grep "ii  kernel.*MEPIS" | head -1 | awk '{print $3}' | sed -e "s/MEPIS.//"`
        elif [ -f "/etc/debian_version" ]
        then
            MYOSNAME="Debian `cat /etc/debian_version`"
            MYOSPATCH=`stat /var/lib/dpkg/info 2> /dev/null | awk '/Modify/ {print $2}'`
        elif [ "`dpkg --list 2> /dev/null`" ]
        then
            MYOSNAME="Debian "`dpkg --list | grep "ii  base-files" | awk '{print $3}'`
        elif [ "`grep "^PRETTY_NAME=" /etc/os-release 2> /dev/null`" ]
        then
            MYOSNAME=`grep "^PRETTY_NAME=" /etc/os-release | cut -f2 -d'"' | sed -e "s/ *[(].*//"`
        elif [ -f "/usr/share/clear/version" ]
        then
             MYOSNAME="Clear Linux `cat /usr/share/clear/version`"
        elif [ -f "/usr/share/clear/version" ]
        then
             MYOSNAME="Clear Linux `cat /usr/share/clear/version`"
        else
            for FILE in `ls -1 /etc/*release 2> /dev/null | egrep -v "/etc/(lsb|os)-release"`
            do
                MYOSNAME="$MYOSNAME
`head -2 $FILE 2> /dev/null | paste - - | sed -e \"s/ Linux / /\" -e \"s/release //\" -e \"s/[(].*[uU]pdate/update/\" -e \"s/[()].*//\" -e \"s/ .*=/ /\" -e \"s/ for.*//\" -e \"s/	/ /g\"`"
            done
            MYOSNAME=`echo "$MYOSNAME" | sort | uniq | paste - - - - | sed -e "s/ *	/, /g" -e "s/^, //" -e "s/[, ]*$//"`
            if [ ! "$MYOSNAME" ]
            then
                MYOSNAME=Unknown
            fi
        fi
        MYOSKERNEL="`uname -r` (`uname -v | sed -e 's/ (.*)//g'`)"
        MYOSBOOT=`isitset \`systemd-analyze 2> /dev/null | grep "^Startup finished in " | sed -e "s/Startup finished in //;s/[^ ]* (firmware) + //;s/[^ ]* (loader) +//;s/ =.*//"\``
        ;;

    *NT*)
        MYOSTYPE="nt"
        if [ ! "`echo \"$WINDIR\" | grep \":/\"`" ]
        then
            WINDIR=`echo "/$WINDIR" | sed -e "s@:\\\\\\@/@"`
        fi
        HARDWARES=`PATH="$WINDIR/system32:$WINDIR/system32/wbem:$PATH"; systeminfo 2> /dev/null`
        MYWINDOW=`echo "$HARDWARES" | grep "^OS Name:" | sed -e "s/^.*: *//" -e "s/(R)//g" -e "s/Microsoft //" -e "s/ $//"`
        SP=`echo "$HARDWARES" | grep "^OS Version:.*Service Pack" | sed -e "s/.*Service Pack //" | awk '{printf(" SP%s\n",$1)}'`
        if [ "$MYWINDOW" ]
        then
            MYOSNAME="$MYWINDOW$SP"
        fi
        MYOSKERNEL="NT "`echo "$HARDWARES" | grep "^OS Version:" | awk '{print $3}'`
        ;;

    OSF1)
        MYOSTYPE="tru64"
        MYOSNAME=`uname -s -r | sed -e "s/V//"`
        ;;

    SunOS)
        MYOSTYPE="solaris"
        MYOSNAME=`uname -s -r`
        case $MYOSNAME in
        SunOS\ 5.*)
            MYOS="$MYOSNAME (Solaris `uname -r | cut -f2 -d\".\"`)"
            ;;
        esac
        ;;

    *)
        MYOSTYPE=`uname -s | tr ^[A-Z] ^[a-z]`
        MYOSNAME="`uname -s -r`"
        ;;
    esac

    case `uname` in
    *NT*)
        MYUPTIME=`isitset \`echo "$HARDWARES" | grep "^System Boot Time:" | sed -e "s/.*: //"\``
        MYLOAD=Unknown
        ;;

    Darwin)
        MYOS="$MYOS (`system_profiler SPSoftwareDataType 2> /dev/null | grep \"System Version\" | sed -e \"s/.*: //\" -e \"s/ [\(].*//\"`)"
        MYUPTIME=`isitset \`uptime 2> /dev/null | cut -f1-2 -d"," | sed -e "s/.*up //"\``
        MYLOAD=`isitset \`uptime 2> /dev/null | sed -e "s/^.*load averages: //"\``
        ;;

    *)  # Avoid buggy uptime
        MYUPTIME=`isitset \`w -u 2> /dev/null | head -1 | cut -f1-2 -d"," | sed -e "s/.*up //" -e "s/(s)//" -e "s/  */ /g"\``
        MYLOAD=`isitset \`w -u 2> /dev/null | head -1 | sed -e "s/^.*load average: //"\``
        ;;
    esac

    case `uname` in
    AIX)
        MYTYPE=`isitset \`lsattr -E -l proc0 2>&1 | grep ^type | awk '{print $2}'\``
        CORES=
        case $MYTYPE in
        PowerPC_POWER[45])
            MYBIT="64bit"
            for PROC in `lsdev -C 2> /dev/null | grep ^proc | sed -e "s/.*proc//" | awk '{print $1}'`
            do
                if [ "`expr $PROC / 2 \* 2`" != "$PROC" ]
                then
                    CORES=2
                    break
                fi
            done
            ;;
        PowerPC_POWER*|PowerPC_RS64*)
            MYBIT="64bit"
            ;;
        *)
            MYBIT="32bit"
            ;;
        esac
        MYTYPEX="ppc"
        if [ "`lsdev -C | grep \"Virtual I/O Bus\"`" ]
        then
            MYCPUS=`isitset \`lsdev -C 2> /dev/null | grep ^proc | wc -l | awk '{print $1}'\``" (Virtual processors)"
        else
            MYCPUS=`isitset \`lsdev -C 2> /dev/null | grep ^proc | wc -l | awk '{print $1}'\``
            if [ "`bindprocessor -q 2> /dev/null | sed -e \"s/.*://\" | wc | awk '{print $2/2}'`" = "$MYCPUS" ]
            then
                if [ "$CORES" ]
                then
                    MYCPUSX="$CORES cores/socket, SMT enabled"
                else
                    MYCPUSX="SMT enabled"
                fi
            elif [ "$CORES" ]
            then
                MYCPUSX="$CORES cores/socket"
            fi
        fi
        MYCLOCK=`pmcycles 2> /dev/null | sed -e "s/.*at //"`
        if [ ! "$MYCLOCK" ]
        then
            MYCLOCK=`isitset \`lsattr -E -l proc0 2>&1 | grep ^frequency | awk '{printf ("%d\n",$2/1000000+0.5)}'\``" MHz"
            if [ "$MYCLOCK" = "Unknown MHz" ]
            then
                cat > /tmp/hardware$$.c 2> /dev/null << EOF
#include <stdio.h>
double rtc(void);
void main() {
  int i, isum, iter, maxiter;
  double freq, maxfreq, time1, time2;
  maxiter = 10;
  maxfreq = 0.0;
  for (iter=0; iter<maxiter; iter++)
  {
    time1 = rtc();
    isum = 0;
    for (i=0; i<100000; i++) isum += 1;
    time2 = rtc();
    freq = 0.9/(time2-time1);
    if (freq > maxfreq) maxfreq = freq;
  }
  printf("CPU Clock = %.0f MHz\n", maxfreq+0.5);
}
EOF
                (cd /tmp; xlc -qnolm /tmp/hardware$$.c -lxlf90 -o /tmp/hardware$$ > /dev/null 2>&1)
                rm -f /tmp/hardware$$.*
                HARDWARES=`/tmp/hardware$$ 2> /dev/null; rm -f /tmp/hardware$$`
                MYCLOCK=`isitset \`echo "$HARDWARES" | grep "CPU Clock" | awk '{print $4}'\``" MHz"
            fi
        fi
        MYBUS=`lsattr -E -l sys0 | grep "System Bus Frequency" | awk '{printf("%d MHz",$2/1000000+0.5)}'`
        if [ "$MYBUS" ]
        then
            MYCLOCK="$MYCLOCK ($MYBUS System Bus)"
        fi
        MYCACHE=`isitset \`lsattr -E -l L2cache0 2>&1 | grep ^size | awk '{print $2}'\``" KB"
        MYCACHEX="L2"
        MYRAM=`isitset \`lsattr -E -l sys0 -a realmem 2> /dev/null | awk '{printf ("%d\n",$2/1024)}'\``" MB"
        MYSWAP=`expr \`lsps -a 2> /dev/null | grep "MB " | awk '{printf "%d + ",$4}'\` \`lsps -a 2> /dev/null | grep "GB " | awk '{printf "%d + ",$4*1024}'\` 0`" MB"
        ;;

    Darwin)
        HARDWARES=`/usr/sbin/sysctl -a | sed -e "s/ = /: /"`
        case `uname -m` in
        i386|amd64|x86_64)
            MYTYPE=`echo "$HARDWARES" | grep "machdep.cpu.brand_string:" | cut -f2- -d":"`
            MYTYPEX="x86"
            ;;
        *ppc*)
            MYTYPE=`echo "$HARDWARES" | grep "machdep.cpu.brand_string:" | cut -f2- -d":"`
            MYTYPEX="ppc"
            ;;
        esac
        if [ "`echo \"$HARDWARES\" | grep \"hw.cpu64bit_capable: 1$\"`" ]
        then
            MYBIT=64bit
        else
            MYBIT=32bit
        fi
        MYCPUS=`echo "$HARDWARES" | grep "machdep.cpu.core_count: " | awk '{print $2}'`
        CORES=`echo "$HARDWARES" | grep "machdep.cpu.cores_per_package: [1-9]" | awk '{print $2}'`
        if [ "$CORES" -gt "$MYCPUS" ]
        then
            CORES="$MYCPUS"
        fi
        SOCKETS=`expr $MYCPUS / $CORES`
        THREADS=`echo "$HARDWARES" | grep "machdep.cpu.thread_count: " | awk '{print $2}'`
        if [ "$CORES" ]
        then
            if [ $MYCPUS != $THREADS ]
            then
                MYCPUSX="$SOCKETS sockets with $CORES cores each, Hyper-threading enabled"
            else
                MYCPUSX="$SOCKETS sockets with $CORES cores each"
            fi
        else
            if [ $MYCPUS != $THREADS ]
            then
                MYCPUSX="Hyper-threading enabled"
            fi
        fi
        if [ $SOCKETS = 1 ]
        then
            MYCPUSX=`echo "$MYCPUSX" | sed -e "s/ sockets / socket /" -e "s/ each//"`
        fi
        MYCLOCK=`echo "$HARDWARES" | grep "hw.cpufrequency:" | awk '{printf("%d MHz",$2/1000000+0.5)}'`
        MYBUS=`echo "$HARDWARES" | grep "hw.busfrequency:" | awk '{printf("%d MHz",$2/1000000+0.5)}'`
        if [ "$MYBUS" ]
        then
            MYCLOCK="$MYCLOCK ($MYBUS System Bus)"
        fi
        MYCACHE=`echo "$HARDWARES" | grep "hw.l2cachesize: " | awk '{printf("%d KB (L2)",$2/1024)}'`
        MYRAM=`echo "$HARDWARES" | grep "hw.memsize:" | awk '{printf("%d MB",$2/1048576)}'`
        MYSWAP=`echo "$HARDWARES" | grep "vm.swapusage: " | sed -e "s/M//g" | awk '{printf("%d MB",$3)}'`
        ;;

    HP-UX)
        if [ "`uname -m`" = ia64 ]
        then
            HARDWARES=`/usr/contrib/bin/machinfo 2> /dev/null`
            MYTYPE=`echo "$HARDWARES" | grep " processor model:" | sed -e "s/.*Intel/Intel/" -e "s/ [pP]rocessor//"`
            MYTYPEX="ia64"
            MYBIT="64bit"
            MYCPUS=`isitset \`echo "$HARDWARES" | grep " Number of CPUs =" | sed -e "s/.* = //"\``
            MYCLOCK=`isitset \`echo "$HARDWARES" | grep " Clock speed =" | sed -e "s/.* = //"\``
            MYCACHE=`isitset \`echo "$HARDWARES" | grep "L2.*size = " | sed -e "s/.*size = //" -e "s/,.*//"\` | sed -e "s/ KB /+/g"`
            MYCACHEX="L2, "`isitset \`echo "$HARDWARES" | grep "L3.*size = " | sed -e "s/.*size = //" -e "s/,.*//"\``" L3"
            MYRAM=`isitset \`echo "$HARDWARES" | grep "Memory = " | sed -e "s/.* = //" -e "s/ (.*//"\``
        else
            cat > /tmp/hardware$$.c 2> /dev/null << EOF
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/param.h>
#include <sys/pstat.h>
#define _PSTAT64
#define MAX_CPU 4096
int main(int argc, char **argv)
{
  long                 clocks_per_second;
  long                 kernel_bit;
  long                 chip_type;
  struct pst_processor buf[MAX_CPU];
  struct pst_static    statbuf;
  int                  num_cpu;
  int                  frequency;
  long sysconf(int name);
  int pstat_getprocessor( struct pst_processor *buf, size_t elemsize, size_t elemcount, int index);
  num_cpu = pstat_getprocessor( &buf[0], (size_t) sizeof(struct pst_processor), (size_t) MAX_CPU, (int) 0);
  clocks_per_second=sysconf(_SC_CLK_TCK);
  frequency = clocks_per_second*(buf[0].psp_iticksperclktick/(1000L))/1000L;
  printf("CPU Count = %d\n",num_cpu);
  printf("CPU Clock = %d MHz\n",frequency);
}
EOF
            (cd /tmp; cc -Ae /tmp/hardware$$.c -o /tmp/hardware$$ > /dev/null 2>&1)
            rm -f /tmp/hardware$$.*
            HARDWARES=`/tmp/hardware$$ 2> /dev/null`
            rm -f /tmp/hardware$$
            MYTYPE="PA8xxx"
            MYTYPEX="hppa"
            MYCPUS=`isitset \`echo "$HARDWARES" | grep "CPU Count" | awk '{print $4}'\``
            if [ "`getconf HW_CPU_SUPP_BITS 2>&1 | grep Invalid`" ]
            then
                MYBIT="32bit"
            else
                MYBIT=`isitset \`getconf HW_CPU_SUPP_BITS 2> /dev/null | sed -e "s@.*/@@"\``"bit"
            fi
            MYCLOCK=`isitset \`echo "$HARDWARES" | grep "CPU Clock" | awk '{print $4}'\``" MHz"
            MYRAM=`isitset \`cat /var/adm/syslog/*syslog.log | grep Physical: | tail -1 | sed -e "s/.*Physical: //" -e "s/ Kbytes.*//" | awk '{printf ("%d\n",$1/1024+0.5)}'\`" MB"`
        fi
        cp /usr/sbin/swapinfo /tmp/swapinfo$$ 2> /dev/null  # Get pass permissions
        MYSWAP=`isitset \`/tmp/swapinfo$$ -t | tail -1 | awk '{printf("%d\n",$2/1024+0.5)}'\``" MB"
        rm -f /tmp/swapinfo$$
        ;;

    IRIX*)
        HARDWARES=`hinv`
        MYTYPE=`isitset \`echo "$HARDWARES" | grep "^CPU" | awk '{print $3}'\``
        MYTYPEX="mips"
        case $MYTYPE in
        R3???)
            MYTYPE="$MYTYPE (MIPS1)"
            MYBIT="32bit"
            ;;
        R40??)
            MYTYPE="$MYTYPE (MIPS2)"
            MYBIT="32bit"
            ;;
        R44??|R46??|R5???)
            MYTYPE="$MYTYPE (MIPS3)"
            MYBIT="32bit"
            ;;
        *)
            MYTYPE="$MYTYPE (MIPS4)"
            MYBIT="64bit"
            ;;
        esac
        MYCPUS=`isitset \`echo "$HARDWARES" | grep "^[1-9].*IP.*Processor" | awk '{print $1}'\``
        MYCLOCK=`isitset \`echo "$HARDWARES" | grep "^[1-9].*IP.*Processor" | awk '{printf ("%s %s\n",$2,$3)}' | sed -e "s/MHZ/MHz/" -e "s/GHZ/GHz/"\``
        MYCACHE=`isitset \`echo "$HARDWARES" | grep "^Secondary.*cache" | sed -e "s/.*: //" -e "s/Mbyte/MB/" -e "s/Gbyte/GB/" | awk '{printf ("%s %s\n", $1, $2)}'\``
        MYCACHEX="L2"
        MYRAM=`isitset \`echo "$HARDWARES" | grep "Main memory size:" | sed -e "s/Main memory size: //" -e "s/Mbytes/MB/" -e "s/Gbytes/GB/"\``
        MYSWAP=`expr \`swap -l | tail +2 | awk '{printf "%d + ",$4}'\` 0 | awk '{printf("%d\n",$1/2048+0.5)}'`" MB"
        ;;

    Linux)
        case `uname -m` in
        ia64)
             MYTYPE=`isitset \`grep ^family /proc/cpuinfo 2> /dev/null | head -1 | sed -e "s/.*: //" -e "s/IA-64/Itanium/"\``
             MYTYPEX="ia64"
             MYBIT="64bit"
             ;;
        ppc64)
            MYTYPE=`isitset \`grep "^cpu" /proc/cpuinfo 2> /dev/null | head -1 | sed -e "s/.*: /PowerPC_/" -e "s/ .*//"\``
            MYTYPEX="ppc"
            MYBIT="64bit"
            ;;
        ppc)
            MYTYPE=`isitset \`grep "^cpu" /proc/cpuinfo 2> /dev/null | head -1 | sed -e "s/.*: /PowerPC_/" -e "s/ .*//"\``
            MYTYPEX="ppc"
            MYBIT="32bit"
            ;;
        sparc64)
            MYTYPE=`isitset \`grep "^model name" /proc/cpuinfo 2> /dev/null | head -1 | sed -e "s/.*: //"\``
            MYTYPEX="sparc"
            MYBIT="64bit"
            ;;
        sparc)
            MYTYPE=`isitset \`grep "^model name" /proc/cpuinfo 2> /dev/null | head -1 | sed -e "s/.*: //"\``
            MYTYPEX="sparc"
            MYBIT="32bit"
            ;;
        x86_64)
            MYTYPE=`isitset \`grep "^model name" /proc/cpuinfo 2> /dev/null | head -1 | sed -e "s/.*: //"\``
            MYTYPEX="x86"
            MYBIT="64bit"
            MYBITSX=`grep "^address sizes" /proc/cpuinfo 2> /dev/null | tail -1 | cut -f2 -d: | awk '{printf("%sbit physical",$1)}'`
            ;;
        i*86|x86)
            if [ "`grep \"^flags.*sse2\" /proc/cpuinfo 2> /dev/null`" ]
            then
                MYTYPE=`isitset \`grep "^model name" /proc/cpuinfo 2> /dev/null | head -1 | sed -e "s/.*: //" -e "s/Intel(R) [Xx][Ee][Oo][Nn]/Intel(R) Pentium(R) 4 XEON/" -e "s/ CPU.*//"\``
            elif [ "`grep \"^flags.*sse\" /proc/cpuinfo 2> /dev/null`" ]
            then
                MYTYPE=`isitset \`grep "^model name" /proc/cpuinfo 2> /dev/null | head -1 | sed -e "s/.*: //" -e "s/Intel(R) [Xx][Ee][Oo][Nn]/Intel(R) Pentium III Xeon/" -e "s/ CPU.*//"\``
            else
                MYTYPE=`isitset \`grep "^model name" /proc/cpuinfo 2> /dev/null | head -1 | sed -e "s/.*: //" -e "s/Intel(R) [Xx][Ee][Oo][Nn]/Intel(R) Pentium II Xeon/" -e "s/ CPU.*//"\``
            fi
            MYTYPEX="x86"
            MYBIT="32bit"
            ;;
        esac
        THREADS=`grep "^processor" /proc/cpuinfo 2> /dev/null | wc -l | awk '{print $1}'`
        LSPCI=`PATH=/sbin:$PATH; lspci 2> /dev/null`
        DEVICES=`($LSPCI; cat /proc/ide/hd?/model /proc/scsi/scsi; /sbin/lsmod) 2> /dev/null`
        CONTAINER=
        VM=
        if [ "`echo \"$DEVICES\" | egrep '^(.*Hyper-V|hv_'`" ]
        then
            VM="Hyper-V"
        elif [ "`echo \"$DEVICES\" | grep '^qemu'`" ]
        then
            VM="QEMU"
        elif [ "`echo \"$DEVICES\" | egrep '^(VBOX|vboxguest)'`" ]
        then
            VM="VirtualBox"
        elif [ "`echo \"$DEVICES\" | egrep '^(VM[Ww]are)|vmw_'`" ]
        then
            VM="VMware"
        elif [ "`echo \"$DEVICES\" | grep '^xen_blkfront'`" ]
        then
            VM="Xen"
        fi

        if [ "`grep /docker/ /proc/1/cgroup 2> /dev/null`" ]
        then
            CONTAINER="Docker `head -1 /proc/1/cgroup | sed -e \"s@.*/docker/\(.\{12\}\).*@\1@\"`"
        elif [ "`grep /lxc/ /proc/1/cgroup 2> /dev/null`" ]
        then
            CONTAINER="LXC"
        fi

        if [ "$VM" ]
        then
            MYCPUS="$THREADS"
            if [ "$CONTAINER" ]
            then
                MYCPUSX="$CONTAINER container, $VM VM"
            else
                MYCPUSX="$VM VM"
            fi
        elif [ "$CONTAINER" ]
        then
            MYCPUS="$THREADS"
            MYCPUSX="$CONTAINER container"
        else
            SOCKETS=`grep "^physical id" /proc/cpuinfo 2> /dev/null | sort | uniq | wc -l | awk '{print $1}'`
            if [ $SOCKETS = 0 ]
            then
                SIBLINGS=`grep "^siblings" /proc/cpuinfo | head -1 | awk '{printf("%d\n",$3)}'`
                if [ "$SIBLINGS" ]
                then
                    SOCKETS=`expr $THREADS / $SIBLINGS`
                else
                    SOCKETS=$THREADS
                fi
            fi
            case $MYTYPE in
            Dual\ Core*)
                CORES=2
                ;;
            Quad-Core*)
                CORES=4
                ;;
            *)
                CORES=`grep "^cpu cores" /proc/cpuinfo | head -1 | awk '{print $4}' | sed -e "s/^1$//"`
                ;;
            esac
            if [ "$CORES" ]
            then
                MYCPUS=`expr $SOCKETS \* $CORES`
                if [ `expr $MYCPUS \* 2` = $THREADS ]
                then
                    MYCPUSX="$SOCKETS sockets with $CORES cores each, Hyper-threading enabled"
                else
                    MYCPUSX="$SOCKETS sockets with $CORES cores each"
                fi
            else
                MYCPUS=$SOCKETS
                if [ $MYCPUS != $THREADS ]
                then
                    MYCPUSX="Hyper-threading enabled"
                fi
            fi
            if [ $SOCKETS = 1 ]
            then
                MYCPUSX=`echo "$MYCPUSX" | sed -e "s/ sockets / socket /" -e "s/ each//"`
            fi
        fi
        MYCLOCK=`isitset \`grep "^cpu MHz" /proc/cpuinfo 2> /dev/null | head -1 | sed -e "s/.*: //" | awk '{printf ("%d\n", $1+0.5)}'\``" MHz"
        if [ "$MYCLOCK" = "Unknown MHz" ]
        then
            MYCLOCK=`isitset \`grep "^clock" /proc/cpuinfo 2> /dev/null | head -1 | sed -e "s/.*: //" | awk '{printf ("%d\n", $1+0.5)}'\``" MHz"
        fi
        if [ -f /proc/pal/cpu0/cache_info ]
        then
            MYCACHE=`isitset \`grep Size /proc/pal/cpu0/cache_info 2> /dev/null | tail -2 | head -1 | awk '{printf "%d KB\n",$3/1024}'\``
            MYCACHEX="L2, "`isitset \`grep Size /proc/pal/cpu0/cache_info 2> /dev/null | tail -1 | awk '{printf "%d KB\n",$3/1024}'\``" L3"
        else
            MYCACHE=`isitset \`grep "^cache size" /proc/cpuinfo 2> /dev/null | head -1 | sed -e "s/.*: //"\``
            MYCACHEX="L2"
        fi
        MYRAM=`isitset \`grep ^MemTotal /proc/meminfo 2> /dev/null | awk '{printf ("%d\n",$2/1024+0.5)}'\``" MB"
        MYRAMX=`grep ^MemAvailable /proc/meminfo 2> /dev/null | awk '{printf ("%d\n",$2/1024+0.5)}'`" available"
        MYSWAP=`grep SwapTotal /proc/meminfo 2> /dev/null | awk '{printf("%d\n",$2/1024+0.5)}'`" MB"
        MYSWAPX=`grep SwapFree /proc/meminfo 2> /dev/null | awk '{printf("%d\n",$2/1024+0.5)}'`" free"
        ;;

    *NT*)
        MYTYPE=`isitset \`set | grep "^PROCESSOR_IDENTIFIER=" | cut -f2 -d"=" | sed -e "s/'//g"\``
        case $PROCESSOR_ARCHITEW6432$PROCESSOR_ARCHITECTURE in
        AMD64)
            MYTYPEX="x86"
            MYBIT="64bit"
            ;;
        x86)
            MYTYPEX="x86"
            MYBIT="32bit"
            ;;
        esac
        MYCPUS=`isitset "$NUMBER_OF_PROCESSORS"`
        case "$HARDWARES" in
        *VirtualBox*)
            MYCPUSX="VirtualBox virtual processors"
            ;;
        *VMware\ *)
            MYCPUSX="VMWare virtual processors"
            ;;
        esac
        MYCLOCK=`isitset \`echo "$HARDWARES" | grep "~.*Mhz" | head -1 | sed -e "s/.*~//" -e "s/ Mhz//"\``" MHz"
        MYRAM=`isitset \`echo "$HARDWARES" | grep "^Total Physical Memory:" | sed -e "s/^.*: *//" -e "s/,//"\``
        MYSWAP=`isitset \`echo "$HARDWARES" | egrep "^Page File: Max Size:|^Virtual Memory: In Use:" | sed -e "s/^.*: *//" -e "s/,//"\``
        ;;

    OSF1)
        MYTYPE=`isitset \`/usr/sbin/psrinfo -v | grep The.*processor | head -1 | awk '{printf ("%s %s %s\n",$2,$3,$4)}' | sed -e "s/alpha/Alpha/"\``
        MYTYPEX="alpha"
        MYBIT="64bit"
        MYCPUS=`isitset \`/usr/sbin/psrinfo -n | sed -e "s/.*= //"\``
        MYCLOCK=`isitset \`/usr/sbin/psrinfo -v | grep The.*processor | head -1 | sed -e "s/.*operates at //" -e "s/,$//"\``
        MYRAM=`isitset \` vmstat -P | grep "^Total Physical Memory" | sed -e "s/.*=//" -e "s/M/MB/" -e "s/G/GB/" | awk '{printf ("%d %s\n",$1+0.5,$2)}'\``
        MYSWAP=`isitset \`/sbin/swapon -s | grep "Allocated space:" | tail -1 | sed -e "s/.*(//" -e "s/).*//" -e "s/MB/ MB/" -e "s/GB/ GB/"\``
        ;;

    SunOS)
        if [ "`uname -m`" = i86pc ]
        then
            MYTYPE=`isitset \`grep "cpu0:" \\\`ls -1tr /var/adm/messages*\\\` | tail -1 | sed -e "s/.*: //"\``
            MYTYPEX="x86"
            if [ -d /lib/amd64 ]
            then
                MYBIT="64bit"
            else
                MYBIT="32bit"
            fi
            MYCPUS=`isitset \`/usr/sbin/prtconf 2> /dev/null | egrep "cpu(, instance| .driver not attached)" | wc -l | awk '{print $1}' | sed -e "s/^0$//"\``
            MYCLOCK=`isitset \`grep "cpu0:.*clock.*Hz" \\\`ls -1tr /var/adm/messages*\\\` | tail -1 | sed -e "s/.*clock //" -e "s/)$//"\``
            MYRAM=`isitset \`/usr/sbin/prtconf 2> /dev/null | grep "^Memory size:" | sed -e "s/^Memory size: //" -e "s/Megabytes/MB/"\``
        else
            HARDWARES=`/usr/platform/\`uname -m\`/sbin/prtdiag 2> /dev/null | sed -e "s/(TM) //"`
            if [ "`echo \"$HARDWARES\" | grep Fujitsu`" ]
            then
                MYTYPE=`isitset \`echo "$HARDWARES" | grep "Fujitsu" | head -1 | sed -e "s/.*SPARC64 /SPARC64-/" -e "s/ [0-9]*.Hz//"\``" ("`echo "$HARDWARES" | grep "Fujitsu" | head -1 | sed -e "s/.*Fujitsu/Fujitsu/" | awk '{printf("%s %s %s\n", $1, $2, $3)}'`")"
``
            elif [ "`echo \"$HARDWARES\" | grep \"Sun Microsystems.*\(\"`" ]
            then
                MYTYPE=`isitset \`echo "$HARDWARES" | grep "Sun Microsystems" | head -1 | cut -f2 -d"(" | cut -f1 -d")" | sed -e "s/.*X //" -e "s/ [0-9]*.Hz//"\``
            else
                case $HARDWARES in
                *UltraSPARC-T*)
                    MYTYPE=`echo "$HARDWARES" | grep "UltraSPARC-T" | head -1 | sed -e "s/.*,//" -e "s/ *\$//"`
                    ;;
                *)
                    MYTYPE=`isitset \`echo "$HARDWARES" | grep " US-" | head -1 | sed -e "s/.*US-/UltraSPARC-/" | awk '{print $1}'\``
                    ;;
                esac
            fi
            MYTYPEX="sparc"
            case $MYTYPE in
            UltraSPARC*|SPARC64*)
                MYBIT="64bit"
                ;;
            SPARC*)
                MYBIT="32bit"
                ;;
            esac
            if [ "`echo \"$HARDWARES\" | grep Fujitsu`" ]
            then
                MYCPUS=`isitset \`echo "$HARDWARES" | grep "Sun Microsystems" | head -1 | sed -e "s/x SPARC.*//" -e "s/.* //"\``
            else
                case $HARDWARES in
                *UltraSPARC-T1*)  # Single socket only
                    MYCPUS=`isitset \`echo "$HARDWARES" | grep "^MB" | wc -l | awk '{printf("%d (%d cores/socket, 4 threads/core)",$1/4,$1/4)}'\``
                    ;;
                *UltraSPARC-T2*)
                    MYCPUS=`isitset \`echo "$HARDWARES" | grep "^MB" | wc -l | awk '{print $1/8}'\``" (8 cores/socket, 8 threads/core)"
                    ;;
                *)
                    MYCPUS=`isitset \`echo "$HARDWARES" | sed -n -e "/^=* CPU/,/^===/p" | egrep " US-|UltraSPARC" | wc -l | awk '{print $1}'\``
                    ;;
                esac
            fi
            case $MYCPUS in
            [0-9]*)
                ;;
            *)  # Correction for no CPU number
                MYCPUS=1
                ;;
            esac
            case $HARDWARES in
            *UltraSPARC-T*)
                MYCLOCK=`isitset \`echo "$HARDWARES" |  grep "^MB/" | head -1 | awk '{print $3}'\`" MHz"`
                ;;
            *\ MB/P0\ *)
                MYCLOCK=`isitset \`echo "$HARDWARES" | grep " MB/P0 " | head -1 | awk '{printf $2}'\``" "`isitset \`echo "$HARDWARES" | grep " MB/P0 " | head -1 | awk '{printf $3}'\``
                MYCACHE=`isitset \`echo "$HARDWARES" | grep " MB/P0 " | head -1 | awk '{printf $4}'\` | sed -e "s/MB/ MB/" -e "s/GB/ GB/"`
                MYCACHEX="L2"
                ;;
            *CPU*Freq*Size*)
                if [ "`echo \"$HARDWARES\" | grep \"^0.*cpu0\"`" ]
                then
                    MYCLOCK=`isitset \`echo "$HARDWARES" | grep "^0.*cpu0" | awk '{printf $2}'\``" "`echo "$HARDWARES" | grep "^0.*cpu0" | head -1 | awk '{printf $3}'`
                    MYCACHE=`isitset \`echo "$HARDWARES" | grep "^0.*cpu0" | awk '{printf $4}'\` | sed -e "s/MB/ MB/" -e "s/GB/ GB/"`" (L2)"
                else
                    MYCLOCK=`isitset \`echo "$HARDWARES" | grep " 0 " | head -1 | awk '{printf $2}'\``" "`echo "$HARDWARES" | grep " 0 " | head -1 | awk '{printf $3}'`
                    MYCACHE=`isitset \`echo "$HARDWARES" | sed -n -e "/^=* CPU/,/^===/p" | head -1 | awk '{printf $4}'\` | sed -e "s/MB/ MB/" -e "s/GB/ GB/"`" (L2)"
                fi
                ;;
            *)
                MYCLOCK=`isitset \`echo "$HARDWARES" | grep " [0A] " | head -1 | sed -e "s/ A / A - /" -e "s/, */,/" | awk '{print $4}'\``" MHz"
                MYCACHE=`isitset \`echo "$HARDWARES" | grep " [0A] " | head -1 | sed -e "s/ A / A - /" -e "s/, */,/" | awk '{print $5}'\``" MB (L2)"
                ;;
            esac
            MYBUS=`echo "$HARDWARES" | grep "System clock frequency:" | sed -e "s/.*: //" -e "s/MHZ/MHz/"`
            if [ "$MYBUS" ]
            then
                MYCLOCK="$MYCLOCK ($MYBUS System Bus)"
            fi
            MYRAM=`echo "$HARDWARES" | grep "Memory size:" | awk '{print $3 $4}' | sed -e "s/GB/ GB/" -e "s/Megabytes/ MB/"`
        fi
        MYSWAP=`expr \`/usr/sbin/swap -l 2> /dev/null | tail +2 | awk '{printf "%d + ",$4}'\` 0 | awk '{printf("%d\n",$1/2048+0.5)}'`" MB"
        ;;
    esac

    # Report hardware information
    if [ ! "$SHORT" ]
    then
        write_output name="OS Type" value="$MYOSTYPE"
    fi
    if [ "$SHORT" = sys -o ! "$SHORT" ]
    then
        write_output name="OS Name" value="$MYOSNAME"
        write_output name="OS Kernel" value="$MYOSKERNEL"
        write_output name="OS Patch" value="$MYOSPATCH"
        write_output name="OS Boot Time" value="$MYOSBOOT"
    fi
    if [ "$SHORT" = cpu -o ! "$SHORT" ]
    then
        write_output name="CPU Type" value="$MYTYPE" comment="$MYTYPEX"
        write_output name="CPU Addressability" value="$MYBIT" comment="$MYBITSX"
        write_output name="CPU Count" value="$MYCPUS" architecture="$MYCPUSX"
        write_output name="CPU Clock" value="$MYCLOCK"
        if [ "$MYCACHE" = "Unknown" ]
        then
            write_output name="CPU Cache" value="$MYCACHE"
        else
            write_output name="CPU Cache" value="$MYCACHE" comment="$MYCACHEX"
        fi
    fi
    if [ "$SHORT" = sys -o ! "$SHORT" ]
    then
        write_output name="System Memory" value="$MYRAM" comment="$MYRAMX"
        write_output name="System Swap Space" value="$MYSWAP" comment="$MYSWAPX"
        write_output name="System Uptime" value="$MYUPTIME"
        write_output name="System Load" value="$MYLOAD" comment="average over last 1min, 5min & 15min"
    fi
    if [ ! "$SHORT" -o "$SHORT" = "dev" ]
    then
        if [ "`uname`" = Linux ]
        then
            scanbus
        fi
    fi
    if [ "`uname`" = Linux ]
    then
        if [ ! "$SHORT" ]
        then
        # Detect loaders
            GLIBC=`ldd /bin/sh | grep libc | sed -e "s/.*=>//" | awk '{print $1}'`
            if [ "$GLIBC" ]
            then
                write_found name="GNU C library" location="$GLIBC" value="`strings $GLIBC 2> /dev/null | grep 'GNU C Library' | head -1 | sed -e 's/.*version//;s/,//;s/[.]$//' | awk '{print $1}'`"
            fi
        fi
        if [ "$SHORT" = sys -o ! "$SHORT" ]
        then
            for LINKER in `ls -1 /lib*/ld-*so* 2> /dev/null`
            do
                write_found name="Dynamic linker" location="$LINKER"
            done
        fi
    fi

    if [ ! "$SHORT" ]
    then
        # Detect X-Windows
        XSET=`PATH=/usr/bin/X11:/usr/openwin/bin:$PATH; xset -q 2> /dev/null`
        if [ "$XSET" ]
        then
            write_found name="X-Display Power" value="`echo \"$XSET\" | grep \" Standby:.* Suspend:.* Off:\" | sed -e "s/.*Standby://" | awk '{printf(\" %ss %ss %ss\n\", $1, $3, $5)}' | sed -e \"s/ 0s/ Off/g\" -e \"s/^ //\"`" comment="DPMS Standby Suspend Off"
            write_found name="X-Keyboard Repeat" value="`echo \"$XSET\" | grep \" auto repeat delay:.* repeat rate:\" | awk '{printf(\"%sms\n\",$4)}'`" comment="`echo \"$XSET\" | grep \" auto repeat delay:.* repeat rate:\" | awk '{printf(\"%s characters per second\n\",$7)}'`"
            write_found name="X-Mouse Speed" value="`echo \"$XSET\" | grep \" acceleration:.* threshold: \" | awk '{print $2}'`" comment="acceleration factor"
            XSCREENSAVER=`echo "$XSET" | grep " timeout:.* cycle:" | awk '{print $2}'`
            if [ "$XSCREENSAVER" != 0 ]
            then
                write_found name="X-Screensaver" value="$XSCREENSAVER" comment="no power saving for LCD but can keep CPU busy"
            fi
        fi
        XRANDR=`xrandr 2> /dev/null`
        if [ "$XRANDR" ]
        then
            write_found name="X-Windows Display" value="$DISPLAY" comment=`echo "$XRANDR" | grep "^Screen .* current " | sed -e "s/.*current //;s/,.*//;s/ //g"`
        else
            XWININFO=`PATH=/usr/bin/X11:/usr/openwin/bin:$PATH; xwininfo -root 2> /dev/null`
            if [ "$XWININFO" ]
            then
                write_found name="X-Windows Display" value="$DISPLAY" comment="`echo \"$XWININFO\" | grep Width: | awk '{print $2}'`x`echo \"$XWININFO\" | grep Height: | awk '{print $2}'`"
            fi
        fi
        echo
    fi
}

#
# Function to write output
#
write_output() {
    TAGS=
    while [ "$1" ]
    do
        TAGS="$TAGS
$1"
        shift
    done
    TAGS=`echo "$TAGS" | egrep -v "^$|=\$" | sed -e "s/▸/ /g" -e "s/  */ /" -e "s/= */=\"/" -e "s/ *\$/\"/"`
    NAME=`echo "$TAGS" | grep "^name=" | cut -f2 -d"\"" | sed -e "s/\$/:                  /" | cut -c1-19`
    if [ "`echo \"$TAGS\" | grep \"^device=\"`" ]
    then
        DEVICE=`echo "$TAGS" | grep "^device=" | cut -f2 -d"\""`
        case $DEVICE in
        /dev/???)
            ;;
        /dev/*)
            if [ ! -e "$DEVICE" ]
            then
                return
            fi
            ;;
        esac
        $ECHO " $NAME\c"
        echo " $TAGS" | grep "^device=" | cut -f2 -d"\"" | awk '{printf(" %-12s",$1)}'
        $ECHO " "`echo "$TAGS" | grep "^value=" | cut -f2 -d"\""`"\c"
    elif [ "`echo \"$TAGS\" | grep \"^location=\"`" ]
    then
        $ECHO " $NAME "`echo "$TAGS" | grep "^location=" | cut -f2 -d"\""`"\c"
        if [ "`echo \"$TAGS\" | grep \"^value=\"`" ]
        then
            $ECHO "  "`echo "$TAGS" | grep "^value=" | cut -f2 -d"\""`"\c"
        fi
    elif [ "`echo \"$TAGS\" | grep \"^value=\"`" ]
    then
        $ECHO " $NAME "`echo "$TAGS" | grep "^value=" | cut -f2 -d"\""`"\c"
    fi
    if [ "`echo \"$TAGS\" | egrep \"^(architecture|comment)=\"`" ]
    then
        $ECHO " ("`echo "$TAGS" | egrep "^(architecture|comment)=" | cut -f2 -d"\""`")\c"
    fi
    echo
}


#
# Main program
#
case $1 in
-c)
    SHORT=cpu
    ;;
-d)
    SHORT=dev
    ;;
-n)
    SHORT=net
    ;;
-s)
    SHORT=sys
    ;;
*)
    SHORT=
    ;;
esac
(detect) 2> /dev/null
echo
