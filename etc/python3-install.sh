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

LIST=$(python3 -m pip list)
for PIP in $(cat ${0%/*}/python3-requirements.txt 2> /dev/null)
do
    MODULE=$(echo "$PIP" | sed -e "s/[>=].*//")
    if [ ! "${MODULE%?=*}" ]
    then
        $INSTALL ${PIP/>=/==}
    fi
done
