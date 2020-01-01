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
    echo $INSTALL $REQUIREMENTS
    $INSTALL $REQUIREMENTS 2>&1 | grep -v "Requirement already satisfied:"
    return ${PIPESTATUS[0]}
}


if [ "$($PYTHON -m pip 2>&1 | grep "No module named pip")" ]
then
    curl https://bootstrap.pypa.io/get-pip.py | $ARG
fi

if [ -w "$($PYTHON -help 2>&1 | grep usage: | awk '{print $2}')" ]
then
    INSTALL="$PYTHON -m pip install --no-warn-script-location"
else
    INSTALL="$PYTHON -m pip install --no-warn-script-location --user"
fi

REQUIREMENTS=
read_requirements "${0%/*}/python-requirements.txt"
VERSION=$($PYTHON --version 2>&1 | grep "^Python [0-9][.][0-9][.]" | awk '{print $2}' | cut -f1-2 -d.)
read_requirements "${0%/*}/python-$VERSION-requirements.txt"
install_packages
exit $?
