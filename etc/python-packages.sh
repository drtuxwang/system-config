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
        for PACKAGE in $(sed -e "s/#.*//" "$1")
        do
            NAME=${PACKAGE%==*}
            if [[ ! $PACKAGE =~ ==None$ ]]
            then
                requirements[$NAME]="$PACKAGE"
            else
                unset requirements[$NAME]
            fi
        done
    fi
}


check_packages() {
    ERROR=
    PACKAGES=$($PYTHON -m pip list 2> /dev/null | awk 'NR>=3 {printf("%s==%s\n", $1, $2)}')
    for PACKAGE in $PACKAGES
    do
        NAME=${PACKAGE%==*}
        if [ -v requirements[$NAME] ]
        then
            REQUIRED=${requirements[$NAME]}
            if [ "$REQUIRED" != "$PACKAGE" -a "$(echo "$REQUIRED" |grep "[>=]=")" ]
            then
                echo $PACKAGE ${REQUIRED#*==} | awk '{printf("%-20s  # Requirement %s\n", $1, $2)}'
                ERROR=1
            fi
        else
            echo $PACKAGE | awk '{printf("%-20s  # Requirement not found\n", $1)}'
        fi
    done
    for PACKAGE in ${requirements[@]}
    do
        if [ ! "$(echo "$PACKAGES" | grep "^${PACKAGE%[>=]=*}==")" ]
        then
            echo "                      # Requirement $PACKAGE"
            ERROR=1
        fi
    done

    for DIR in $($PYTHON -m site | grep site-packages | cut -f2 -d"'")
    do
        for FILE in $(awk '/^[^_]/ {print $1}' $DIR/*.dist-info/top_level.txt 2> /dev/null)
        do
            if [ ! "$(ls $DIR/$FILE $DIR/$FILE.* 2> /dev/null)" ]
            then
                grep $FILE $DIR/*.dist-info/top_level.txt
                ERROR=1
            fi
        done
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

    echo "$INSTALL --no-warn-script-location" ${requirements[pip]} ${requirements[setuptools]} ${requirements[wheel]}
    $INSTALL ${requirements[pip]} ${requirements[setuptools]} ${requirements[wheel]} 2>&1 | egrep -v "already satisfied:|pip version|--upgrade pip"
    [[ ${PIPESTATUS[0]} = 0 ]] || exit 1
    echo -e "${esc}[33mInstalled!${esc}[0m"
}


install_packages() {
    export CRYPTOGRAPHY_DONT_BUILD_RUST=1

    echo "$INSTALL --no-warn-script-location ${requirements[@]}"
    $INSTALL --no-warn-script-location ${requirements[@]} 2>&1 | egrep -v "already satisfied:|pip version|--upgrade pip"
    [[ ${PIPESTATUS[0]} = 0 ]] || exit 1
    echo -e "${esc}[33mInstalled!${esc}[0m"
}


umask 022
INSTALL="$PYTHON -m pip install"
[[ -w "$($PYTHON -help 2>&1 | grep usage: | awk '{print $2}')" ]] || INSTALL="$INSTALL --user"
[[ "$(uname)" = Darwin ]] && export PKG_CONFIG_PATH="/usr/local/opt/openssl/lib/pkgconfig:/usr/local/opt/zlib/lib/pkgconfig"

declare -A requirements
PYTHON_VERSION=$($PYTHON --version 2>&1 | awk '/^Python [1-9]/{print $2}' | cut -f1-2 -d.)
read_requirements "${0%/*}/python-requirements.txt"
read_requirements "${0%/*}/python$PYTHON_VERSION-requirements.txt"

[[ "$MODE" ]] && install_pip
[[ "$MODE" = install ]] && install_packages
[[ "$MODE" != piponly ]] && check_packages

exit 0
