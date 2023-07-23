#!/usr/bin/env bash
#
# Check debs are defined in Build AppImage using "appimage-builder"
#

set -eu

if [ $# = 0 ]
then
    echo "Usage: $0 <file.yaml>"
    exit 1
fi

WARNINGS=
for PACKAGE in $(ls -1 appimage-build/apt/archives/*.deb 2> /dev/null | sed -e "s@.*/@@;s/_.*//")
do
    [ "$(grep -E "^ *- (-t +[^ ]+ |)${PACKAGE//+/\\+} *$" "$1")" ] || WARNINGS="$WARNINGS $PACKAGE"
done
if [ "$WARNINGS" ]
then
    echo -e "Warning: Not defined in $1\c"
    echo "$WARNINGS" | sed -e "s/ /\\n#    - /g"
fi
