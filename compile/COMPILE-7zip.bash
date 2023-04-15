#!/usr/bin/env bash

# Fix "Dangerous link path was ignored" bug
sed -i "s/if (!IsSafePath(relatPath))/if (0)/" CPP/7zip/UI/Common/ArchiveExtractCallback.cpp

if [ $(uname) = Darwin ]
then
    # https://sourceforge.net/p/sevenzip/discussion/45797/thread/9c2d9061ce/#01e7
    sed -i "s/sysmacros.h/types.h/" CPP/7zip/UI/Common/UpdateCallback.cpp
    sed -i "s/sysmacros.h/types.h/" CPP/7zip/Common/FileStreams.cpp
    # Fixes "-Werror,-Wc++11-extensions", "-Werror,-Wunused-but-set-variable", "-Werror,-Wunreachable-code-return"
    sed -i "s/-Wno-unused-macros \\\/-Wno-unused-macros -Wno-c++11-extensions -Wno-unused-but-set-variable -Wno-unreachable-code-return \\\/" CPP/7zip/warn_clang_mac.mak
    DISABLE_RAR_COMPRESS=1 make -C CPP/7zip/Bundles/Alone2 -f ../../cmpl_mac_x64.mak
elif [ "$(asmc --version 2>&1 | grep "Asmc Macro Assembler")" ]
then
    # https://github.com/nidud/asmc
    make -C CPP/7zip/Bundles/Alone2 -f ../../cmpl_gcc_x64.mak
else
    make -C CPP/7zip/Bundles/Alone2 -f makefile.gcc
fi

FILE=$(find -name 7zz)
ls -l $FILE
strip $FILE
ls -l $FILE
