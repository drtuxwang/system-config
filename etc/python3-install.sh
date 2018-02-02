#!/bin/bash
#
# Check pip modules and install minimum version required
#

if [ -w "$(python3 -help 2>&1 | grep usage: | awk '{print $2}')" ]
then
    INSTALL="python3 -m pip install"
else
    INSTALL="python3 -m pip install --user"
fi

echo "Processing \"${0%/*}/python3-requirements.txt\"..."
umask 022
python3 -m pip install --upgrade pip 2>&1 | grep -v "Requirement already satisfied:"
PACKAGES=$(cat ${0%/*}/python3-requirements.txt 2> /dev/null)
$INSTALL ${PACKAGES//>=/==} 2>&1 | grep -v "Requirement already satisfied:"
