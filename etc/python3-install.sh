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

umask 022
python3 -m pip install --upgrade pip
for PIP in $(cat ${0%/*}/python3-requirements.txt 2> /dev/null)
do
    $INSTALL ${PIP/>=/==}
done
