#!/bin/bash -u
#
# Check pip modules and install minimum version required
#

# Optional input environment
PYTHON=${1-}
FLAG=${2-}

if [ ! -x "$PYTHON" ]
then
    echo "Usage: $0 /path/bin/<python>"
    exit 1
fi


read_requirements() {
    while [ $# != 0 ]
    do
        echo "Processing \"$1\"..."
        for PACKAGE in $(sed -e "s/#.*//;s/>=/==/g" $1)
        do
            NAME=${PACKAGE%==*}
            VERSION=${PACKAGE#*==}
            REQUIREMENTS=$(echo "$REQUIREMENTS" | grep -v "^$NAME=="; echo "$NAME==$VERSION" | grep -v ==None)
        done
        shift
    done
}


install_pip() {
    case $PYTHON_VERSION in
    2.[67]|3.[345])
        GETPIP="https://bootstrap.pypa.io/$PYTHON_VERSION/get-pip.py"
        ;;
    *)
        GETPIP="https://bootstrap.pypa.io/get-pip.py"
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
    echo "Installed!"
}


install_packages() {
    export CRYPTOGRAPHY_DONT_BUILD_RUST=1

    echo "$INSTALL --no-warn-script-location "$REQUIREMENTS
    $INSTALL --no-warn-script-location $REQUIREMENTS 2>&1 | egrep -v "already satisfied:|pip version|--upgrade pip"
    [[ ${PIPESTATUS[0]} = 0 ]] || exit 1
    echo "Installed!"
}


umask 022
INSTALL="$PYTHON -m pip install"
[[ -w "$($PYTHON -help 2>&1 | grep usage: | awk '{print $2}')" ]] || INSTALL="$INSTALL --user"
[[ "$(uname)" = Darwin ]] && export PKG_CONFIG_PATH="/usr/local/opt/openssl/lib/pkgconfig:/usr/local/opt/zlib/lib/pkgconfig"

REQUIREMENTS=
PYTHON_VERSION=$($PYTHON --version 2>&1 | awk '/^Python [1-9]/{print $2}' | cut -f1-2 -d.)
read_requirements "${0%/*}/python-requirements.txt" "${0%/*}/python-requirements_$PYTHON_VERSION.txt"

install_pip
[[ "$FLAG" != piponly ]] && install_packages
exit 0
