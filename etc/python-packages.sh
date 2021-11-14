#!/bin/bash -u
#
# Install/check Python packages requirements
#

# Process options
help() {
    echo "Usage: $0 [-pip|-i] <python>"
    exit 1
}
MODE=
PYTHON=
while [ $# != 0 ]
do
    case $1 in
    -pip)
        MODE="piponly"
        ;;
    -i)
        MODE="install"
        ;;
    -*)
        help
        ;;
    *)
        PYTHON="$1"
        ;;
    esac
    shift
done
if [[ ! /$PYTHON =~ /python[1-9]* ]]
then
    echo "Usage: $0 [-pip|-i] <python>"
    exit 1
fi

esc=$'\033'
export PYTHONPATH=


read_requirements() {
    if [ -f "$1" ]
    then
        echo -e "${esc}[34mProcessing \"$1\"...${esc}[0m"
        for PACKAGE in $(sed -e "s/^#* *//;s/#.*//" "$1" |grep -v "==None")
        do
            NAME=${PACKAGE%==*}
            VERSION=${PACKAGE#*==}
            REQUIREMENTS=$(echo "$REQUIREMENTS" | grep -v "^$NAME=="; echo "$NAME==$VERSION")
        done
        DISABLED=$(grep "==None" $1 | sed -e "s/==.*//;s/.* //" | awk '{printf("%s|", $1)}')
        REQUIREMENTS=$(echo "$REQUIREMENTS" | egrep -v "^($DISABLED)[>=]")
    fi
}


check_packages() {
    ERROR=
    PACKAGES=$($PYTHON -m pip list 2> /dev/null | awk 'NR>=3 {printf("%s==%s\n", $1, $2)}')
    for PACKAGE in $PACKAGES
    do
        if [ ! "$(echo "$REQUIREMENTS" | grep "^${PACKAGE}$")" ]
        then
            echo $PACKAGE | awk '{printf("%-20s  # ", $1)}'
            REQUIRED=$(echo "$REQUIREMENTS" | grep "^${PACKAGE%==*}[>=]")
            if [ "$REQUIRED" ]
            then
                echo "Requirement $REQUIRED"
                ERROR=1
            else
                echo "Requirement not found"
            fi
        fi
    done
    for PACKAGE in $REQUIREMENTS
    do
        if [ ! "$(echo "$PACKAGES" | grep "^${PACKAGE%[>=]=*}==")" ]
        then
            echo "                      # Requirement $PACKAGE"
            ERROR=1
        fi
    done
    [[ "$ERROR" ]] && echo -e "${esc}[31mError!${esc}[0m" && exit 1

    echo -e "${esc}[33mChecked!${esc}[0m"
}


install_pip() {
    case $PYTHON_VERSION in
    2.[67]|3.[345])
        GETPIP="https://bootstrap.pypa.io/pip/$PYTHON_VERSION/get-pip.py"
        ;;
    *)
        GETPIP="https://bootstrap.pypa.io/pip/get-pip.py"
        ;;
    esac

    if [ ! "$($PYTHON -m pip --version 2>&1 | grep "^pip ")" ]
    then
        echo "curl --location --progress-bar $GETPIP | $PYTHON"
        curl --location --progress-bar $GETPIP | $PYTHON || exit 1
        echo "Installed!"
    fi

    echo "$INSTALL --no-warn-script-location "$(echo "$REQUIREMENTS" | egrep "^(pip|wheel)==")
    $INSTALL $(echo "$REQUIREMENTS" | egrep "^(pip|wheel)==") 2>&1 | egrep -v "already satisfied:|pip version|--upgrade pip"
    [[ ${PIPESTATUS[0]} = 0 ]] || exit 1
    echo -e "${esc}[33mInstalled!${esc}[0m"
}


install_packages() {
    export CRYPTOGRAPHY_DONT_BUILD_RUST=1

    echo "$INSTALL --no-warn-script-location "$REQUIREMENTS
    $INSTALL --no-warn-script-location $REQUIREMENTS 2>&1 | egrep -v "already satisfied:|pip version|--upgrade pip"
    [[ ${PIPESTATUS[0]} = 0 ]] || exit 1
    echo -e "${esc}[33mInstalled!${esc}[0m"
}


umask 022
INSTALL="$PYTHON -m pip install"
[[ -w "$($PYTHON -help 2>&1 | grep usage: | awk '{print $2}')" ]] || INSTALL="$INSTALL --user"
[[ "$(uname)" = Darwin ]] && export PKG_CONFIG_PATH="/usr/local/opt/openssl/lib/pkgconfig:/usr/local/opt/zlib/lib/pkgconfig"

REQUIREMENTS=
PYTHON_VERSION=$($PYTHON --version 2>&1 | awk '/^Python [1-9]/{print $2}' | cut -f1-2 -d.)
read_requirements "${0%/*}/python-requirements.txt"
read_requirements "${0%/*}/python$PYTHON_VERSION-requirements.txt"

[[ "$MODE" ]] && install_pip
[[ "$MODE" = install ]] && install_packages
[[ "$MODE" != piponly ]] && check_packages

exit 0
