#!/usr/bin/env bash

cd ${0%/*}
umask 022

VERSION=$(grep "define PY_VERSION " Include/patchlevel.h | cut -f2 -d'"')
MAJOR_VER=${VERSION%.*}
DEFAULT_PYTHON=3.13

if [ "$(gcc --version 2>&1 | grep -E "gcc .* ([1-3][.]|4[.][1-6])")" ]
then
    echo "Error: Unsupported old compiler version"
    exit 1
fi

case $(uname) in
Darwin)
    export CPPFLAGS="-I/usr/local/opt/openssl@1.1/include $CPPFLAGS"
    export LDFLAGS="-L/usr/local/opt/openssl@1.1/lib $LDFLAGS"
    export PKG_CONFIG_PATH="/usr/local/opt/openssl@1.1/lib/pkgconfig:$PKG_CONFIG_PATH"

    export CPPFLAGS="-I/usr/local/opt/sqlite/include $CPPFLAGS"
    export LDFLAGS="-L/usr/local/opt/sqlite/lib $LDFLAGS"

    export CPPFLAGS="-I/usr/local/opt/tcl-tk/include $CPPFLAGS"
    export LDFLAGS="-L/usr/local/opt/tcl-tk/lib $LDFLAGS"

    export CPPFLAGS="-I/usr/local/opt/zlib/include $CPPFLAGS"
    export LDFLAGS="-L/usr/local/opt/zlib/lib $LDFLAGS"

    WRAPPER="#!/usr/bin/env bash

PYTHON_LIB=\$(realpath \"\${0%/*}/../lib\" | sed -e \"s,bin/[^/]*$,lib,\")
export DYLD_LIBRARY_PATH=\"\$PYTHON_LIB:\$DYLD_LIBRARY_PATH\"
export LDFLAGS=\"-L\$PYTHON_LIB\"
exec \"\${0%/*}/python$VERSION\" \"\$@\""
    ;;
*)
    if [[ ${0##/*} =~ COMPILE32* ]]
    then
        export CPPFLAGS="-m32"
        export CFLAGS="-m32"
        export LDFLAGS="-m32"
    fi

    WRAPPER="#!/usr/bin/env bash

PYTHON_LIB=\$(realpath \"\${0%/*}/../lib\" | sed -e \"s,bin/[^/]*$,lib,\")
export LD_LIBRARY_PATH=\"\$PYTHON_LIB:\$LD_LIBRARY_PATH\"
export LDFLAGS=\"-L\$PYTHON_LIB\"
exec \"\${0%/*}/python$VERSION\" \"\$@\""
    ;;
esac
# Missing realpath on old operating systems
realpath --version || WRAPPER=$(echo "$WRAPPER" | sed -e "s/realpath/readlink -e/")

# Disable tests due to memory leaks requiring > 16GB
if [ "$MAJOR_VER" != 3.14 ]
then
    sed -i "s/  'test_functools',/  # 'test_functools',/" Lib/test/libregrtest/pgo.py
    sed -i "s/  'test_json',/  # 'test_json',/" Lib/test/libregrtest/pgo.py
fi

CONFIGURE="./configure --prefix="$PWD/install" --enable-ipv6 --enable-shared"
# Enable profile-guided optimization (PGO) except old gcc
[ "$(gcc --version 2>&1 | grep "gcc .* [1-8][.]")" ] || CONFIGURE="$CONFIGURE --enable-optimizations"
# Enable link time optimizations (LTO) except old gcc
[ "$(gcc --version 2>&1 | grep "gcc .* [1-4][.]")" ] || CONFIGURE="$CONFIGURE --with-lto"

$CONFIGURE
make
make install

if [ -d install/bin ]
then
    # Fix readonly permission on some libraries
    chmod -R u+w install

    # Make relocatable executable
    if [ ! "$(grep "#!/usr/bin/env bash" install/bin/python$MAJOR_VER)" ]
    then
        mv install/bin/python$MAJOR_VER install/bin/python$VERSION
        echo "$WRAPPER" > install/bin/python$MAJOR_VER
        chmod 755 install/bin/python$MAJOR_VER
    fi

    # Make relocatable scripts
    for FILE in $(cd install/bin; ls -1 | grep -v "*.py$")
    do
        if [ "$(grep "^#!/.*/python$MAJOR_VER" "install/bin/$FILE")" ]
        then
            PYFILE=$(echo "$FILE.py" | sed -e "s/-$MAJOR_VER//" -e "s/[.][1-9][0-9]*m*//")
            sed -e "1s@^#.*@#!/usr/bin/env python$MAJOR_VER@" "install/bin/$FILE" > "install/bin/$PYFILE"
            rm -f "install/bin/$FILE"
            echo "#!/usr/bin/env bash
MYDIR=\${0%/*}
exec \"\$MYDIR/python$MAJOR_VER\" \"\$MYDIR/$PYFILE\" \"\$@\"" > "install/bin/$FILE"
            chmod 755 "install/bin/$FILE"
        fi
    done
    sed -i "s@^prefix=.*@prefix=\${0%/*/*}@;s@\".*/install/lib@\"\$prefix/lib@" "install/bin/python$MAJOR_VER-config"

    # Fix for porting on Ubuntu and running on RHEL
    [ "$(uname)" = Linux ] && sed -i "s/libbz2.so.1.0/libbz2.so.1\x00\x00/" install/lib/python*/lib-dynload/*bz2*.so

    # Non default python3
    [ "$MAJOR_VER" != "$DEFAULT_PYTHON" ] && rm -f install/bin/python3

    # Remove tests
    find install/lib/python* -type f -name '*test*.py' | grep "/[^/]*test[^/]*/" | sed -e "s/\/[^\/]*$//" | uniq | xargs rm -rf
fi

ls -ld $PWD/install/bin/python* $PWD/install/lib/libpython*
grep MODULE.*=missing config.log
