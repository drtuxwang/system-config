#!/bin/bash
#
# Check pip modules and install minimum version required
#

case $1 in
*/python3|*/python3.*)
    if [ "$($1 -m pip 2>&1 | grep "No module named pip")" ]
    then
        curl https://bootstrap.pypa.io/get-pip.py | $1
    fi

    if [ -w "$($1 -help 2>&1 | grep usage: | awk '{print $2}')" ]
    then
        INSTALL="$1 -m pip install"
    else
        INSTALL="$1 -m pip install --user"
    fi

    echo "Processing \"${0%/*}/python3-requirements.txt\"..."
    umask 022
    $INSTALL --upgrade pip 2>&1 | grep -v "Requirement already satisfied:"
    PACKAGES=$(cat ${0%/*}/python3-requirements.txt 2> /dev/null)
    $INSTALL ${PACKAGES//>=/==} 2>&1 | grep -v "Requirement already satisfied:"
    ;;
*)
    echo "Usage: $0 /path/python3.x"
    exit 1
    ;;
esac
