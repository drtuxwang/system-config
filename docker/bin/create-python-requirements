#!/usr/bin/env bash

set -eu

VERSION=${1:-}

TOPDIR=$(realpath "$0" | sed -e "s|/[^/]*/[^/]*/[^/]*$||")
umask 022
rm -rf tmpdir/*python-requirements*

mkdir -p tmpdir
echo "Creating \"tmpdir/install-python-requirements.sh\"..."
cp -p "$TOPDIR"/etc/install-python-requirements.sh tmpdir
echo "Creating \"tmpdir/python-requirements.txt\"..."
cp -p "$TOPDIR"/etc/python-requirements.txt tmpdir

if [ -f "$TOPDIR"/etc/python-requirements_$VERSION.txt ]
then
    echo "Creating \"tmpdir/python-requirements_$VERSION.txt\"..."
    cp -p "$TOPDIR"/etc/python-requirements_$VERSION.txt tmpdir
fi

# Fix group and others file/directory read access recursively
for FILE in $(find tmpdir -type f)
do
    if [ -x "$FILE" ]
    then
        chmod 755 $FILE
    else
        chmod 644 $FILE
    fi
done
