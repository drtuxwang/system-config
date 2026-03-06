#!/usr/bin/env bash
#
# 7-Zip 26.00 (Official) source code & Windows portable app
#

set -e


source_settings() {
    NAME="7zip"
    VERSION="26.00"
    PORT="source-cpp"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://www.7-zip.org/a/7z2600-src.tar.xz
    "
    APP_SHELL="
        cp -p ${0%/*}/../compile/COMPILE-7zip.bash .
        touch -r DOC/readme.txt COMPILE-7zip.bash
    "
}

windows_settings() {
    NAME="7zip"
    VERSION="26.00"
    PORT="windows-x86"

    APP_DIRECTORY="${NAME}_$VERSION-$PORT"
    APP_FILES="
        https://www.7-zip.org/a/7z${VERSION//./}.exe
    "
    APP_REMOVE="
        7-zip.chm
        7-zip.dll
        7zCon.sfx
        7zFM.exe
        7zG.exe
        Lang
        Uninstall.exe
        descript.ion
    "
    APP_SHELL='
        mkdir -p ../bin
        cat << EOF > 7z.bat
@echo off

if "%1"=="a" goto exec
if "%1"=="l" goto exec
if "%1"=="t" goto exec
if "%1"=="x" goto exec
    %~dp0\7z.exe a -m0=lzma2 -mmt=2 -mx=9 -myx=9 -md=128m -mfb=256 -ms=on -snh -snl -stl -y %*
    goto exit
:exec
    %~dp0\7z.exe %1 %2 %3 %4 %5 %6 %7 %8 %9
    goto exit
:exit
EOF
        cat << EOF > un7z.bat
@echo off

if "%1"=="-v" goto view
    %~dp0\7z.exe x -y %*
    goto exit
:view
    %~dp0\7z.exe l %2 %3 %4 %5 %6 %7 %8 %9
    goto exit
:exit
EOF
        cat << EOF > ../bin/7z.bat
@echo off
%~dp0..\7zip_'$VERSION'-windows-x86\7z.bat %*
EOF
        cat << EOF > ../bin/un7z.bat
@echo off
%~dp0..\7zip_'$VERSION'-windows-x86\un7z.bat %*
EOF
        touch -r 7z.exe 7z.bat un7z.bat ../bin/7z.bat ../bin/un7z.bat
    '
    APP_START="helm"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    exec "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" source_settings windows_settings
