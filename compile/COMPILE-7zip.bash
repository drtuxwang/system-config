#!/usr/bin/env bash

cd ${0%/*}
umask 022

# Compile 7zzs as well
export COMPL_STATIC=1

# Fix "Dangerous link path was ignored" (older versions)
sed -i "s/if (!IsSafePath(.*/if (0)/" CPP/7zip/UI/Common/ArchiveExtractCallback.cpp
# Fix "Dangerous link path was ignored"
# Fix "Dangerous link via another link was ignored"
sed -i "s/isDang = true/isDang = false/" CPP/7zip/UI/Common/ArchiveExtractCallback.cpp
# Stop removing "/" from absolute symlink
sed -i "s@^ *Remove_AbsPathPrefixes()@  // Remove_AbsPathPrefixes()@" CPP/7zip/UI/Common/ArchiveExtractCallback.cpp

if [ $(uname) = Darwin ]
then
    # https://sourceforge.net/p/sevenzip/discussion/45797/thread/9c2d9061ce/#01e7
    sed -i "s/sysmacros.h/types.h/" CPP/7zip/UI/Common/UpdateCallback.cpp
    sed -i "s/sysmacros.h/types.h/" CPP/7zip/Common/FileStreams.cpp
    # Disable some warnings
    NOWARN="-Wno-unreachable-code-return -Wno-declaration-after-statement -Wno-unused-but-set-variable"
    sed -i "s/-Wno-poison-system-directories.*/-Wno-poison-system-directories $NOWARN/" CPP/7zip/warn_clang_mac.mak

    COMPL_STATIC= DISABLE_RAR_COMPRESS=1 make -C CPP/7zip/Bundles/Alone2 -f ../../cmpl_mac_x64.mak
elif [ "$(asmc --version 2>&1 | grep "Asmc Macro Assembler")" ]
then
    # https://github.com/nidud/asmc
    make -C CPP/7zip/Bundles/Alone2 -f ../../cmpl_gcc_x64.mak
else
    make -C CPP/7zip/Bundles/Alone2 -f makefile.gcc
fi

FILES=$(find $PWD -name 7zz*)
ls -l $FILES
strip $FILES
ls -l $FILES

# Test for absolute path symlink archiving bug
FILE=$(find $PWD -name 7zzs)
[ ! "$FILE" ] && exit 1
ln -snf /absolute/path testlink
"$FILE" a -snl test.7z testlink > /dev/null || exit 1
rm -f testlink
"$FILE" x test.7z > /dev/null || exit 1
LINK=$(readlink testlink)
if [ "$LINK" != /absolute/path ]
then
    echo "CRITICAL: Unpatched symlink archiving design flaw: $LINK != /absolute/path"
    exit 1
fi
