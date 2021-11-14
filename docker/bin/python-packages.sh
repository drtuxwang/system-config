#!/usr/bin/env bash

set -eu

VERSION=${1:-}

TOPDIR=$(realpath "$0" | sed -e "s|/[^/]*/[^/]*/[^/]*$||")
umask 022
rm -rf tmpdir/*python*requirements.txt

mkdir -p tmpdir
echo "Creating \"tmpdir/python-packages.sh\"..."
cp -p "$TOPDIR"/etc/python-packages.sh tmpdir
echo "Creating \"tmpdir/python-requirements.txt\"..."
cp -p "$TOPDIR"/etc/python-requirements.txt tmpdir

if [ -f "$TOPDIR"/etc/python$VERSION-requirements.txt ]
then
    echo "Creating \"tmpdir/python$VERSION-requirements.txt\"..."
    cp -p "$TOPDIR"/etc/python$VERSION-requirements.txt tmpdir
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
