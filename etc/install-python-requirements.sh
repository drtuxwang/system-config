#!/bin/bash -u
#
# Check pip modules and install minimum version required
#

# Optional input environment
PYTHON=${1-}

if [ ! -x "$PYTHON" ]
then
    echo "Usage: $0 /path/bin/<python>"
    exit 1
fi


read_requirements() {
    if [ -f "$1" ]
    then
        echo "Processing \"$1\"..."
        for PACKAGE in $(sed -e "s/#.*//;s/>=/==/g" $1)
        do
            NAME=${PACKAGE%==*}
            VERSION=${PACKAGE#*==}
            REQUIREMENTS=$(echo "$REQUIREMENTS" | grep -v "^$NAME=="; echo "$NAME==$VERSION" | grep -v ==None)
        done
    fi
}


install_packages() {
    umask 022
    if [ "$(uname)" = Darwin ]
    then
        export PKG_CONFIG_PATH="/usr/local/opt/openssl/lib/pkgconfig:/usr/local/opt/zlib/lib/pkgconfig"
    fi

    $INSTALL $(echo "$REQUIREMENTS" | egrep "^(pip|wheel)==") 2>&1 | egrep -v "already satisfied:|pip version|--upgrade pip"
    $INSTALL $REQUIREMENTS 2>&1 | egrep -v "already satisfied:|pip version|--upgrade pip"
    [[ ${PIPESTATUS[0]} = 0 ]] && echo "Installed!"
    return ${PIPESTATUS[0]}
}


if [ -w "$($PYTHON -help 2>&1 | grep usage: | awk '{print $2}')" ]
then
    INSTALL="$PYTHON -m pip install --no-warn-script-location"
else
    INSTALL="$PYTHON -m pip install --no-warn-script-location --user"
fi

export CRYPTOGRAPHY_DONT_BUILD_RUST=1

REQUIREMENTS=
read_requirements "${0%/*}/python-requirements.txt"
VERSION=$($PYTHON --version 2>&1 | grep "^Python [0-9][.][0-9][.]" | awk '{print $2}' | cut -f1-2 -d.)
read_requirements "${0%/*}/python-requirements_$VERSION.txt"
install_packages
exit $?
