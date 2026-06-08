#!/usr/bin/env bash
#
# 7-Zip 26.01 (Official) source code & Windows portable app
#

set -e


source_settings() {
    NAME="7zip"
    VERSION="26.01"
    PORT="source-cpp"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://www.7-zip.org/a/7z${VERSION//./}-src.tar.xz
        ${0%/*}/../compile/COMPILE-7zip.bash
    "
    APP_SHELL="
        touch -r DOC/readme.txt COMPILE-7zip.bash
    "
}

windows_settings() {
    NAME="7zip"
    VERSION="26.01"
    PORT="windows-x86"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://www.7-zip.org/a/7z${VERSION//./}.exe
        ${0%.*}/7z.bat
        ${0%.*}/un7z.bat
    "
    APP_SHELL="
        7z x -y -snld 7z[1-9]*.exe
        mkdir -p ../bin
        sed -e 's/{{ version }}/$VERSION/' ${0%.*}/7z.bat-bin > ../bin/7z.bat
        sed -e 's/{{ version }}/$VERSION/' ${0%.*}/un7z.bat-bin > ../bin/un7z.bat
        chmod 755 ../bin/7z.bat ../bin/un7z.bat
        touch -r 7z.exe 7z.bat un7z.bat ../bin/7z.bat ../bin/un7z.bat ../bin
    "
    APP_REMOVE="
        7z[1-9]*.exe
        7-zip.chm
        7-zip.dll
        7zCon.sfx
        7zFM.exe
        7zG.exe
        Lang
        Uninstall.exe
        descript.ion
    "
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    exec "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" "$@" source_settings windows_settings
