#!/bin/bash


VERSION=$(uname -r | cut -f1-2 -d. | awk '{printf("%s\n", $1*10)}')
DIR=${0%/config/*}/software

install() {
    INSTALLER=$(ls -1t ""$1"" | head -1)
    echo "Running \"$INSTALLER\" installer..." | sed -e "s/\//\\\\/g"
    $2 "$INSTALLER" -oc:/software -y
}


install "$DIR/system-config_*_generic.exe"
install "$DIR/vim_*_win51x86.exe"

if [ $VERSION -ge 60 ]
then
    install "$DIR/python-minimal_3.*_win60x86.exe"
    if [ $VERSION -lt 100 ]
    then
        install "$DIR/vc-redist_14.*_win51x86.exe"
    else
        echo "Running \"netplwiz\" to remove \"Users must enter user and password\"..."
        if [ -f "c:/Program Files/Oracle/VirtualBox Guest Additions/VBoxGuest.inf" ]
        then
            echo "  (VM password is \Passw0rd!\""
        fi
        cmd /r netplwiz
    fi
fi

echo "Running \"net use s: \\\\vboxsvr\\shared\"..."
net use s: \\vboxsvr\shared > nul 2> nul

if [ "$PROCESSOR_ARCHITECTURE" = AMD64 -o "$PROCESSOR_ARCHITEW6432" = AMD64 ]
then
    INSTALLER=$(ls -1t "$DIR"/virtualbox-additions_*_win6451x86.exe | head -1)
else
    INSTALLER=$(ls -1t "$DIR"/virtualbox-additions_*_win51x86.exe | head -1)
fi
echo "Running \"$INSTALLER\" installer..." | sed -e "s/\//\\\\/g"
cmd /r "$INSTALLER"
