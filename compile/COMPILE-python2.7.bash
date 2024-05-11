#!/usr/bin/env bash

cd ${0%/*}
umask 022

VERSION=$(grep "define PY_VERSION " Include/patchlevel.h | cut -f2 -d'"')
MAJOR_VER=${VERSION%.*}

case $(uname) in
Darwin)
    export CPPFLAGS="-I/usr/local/opt/bzip2/include $CPPFLAGS"
    export LDFLAGS="-L/usr/local/opt/bzip2/lib $LDFLAGS"

    export CPPFLAGS="-I/usr/local/opt/ncurses/include $CPPFLAGS"
    export LDFLAGS="-L/usr/local/opt/ncurses/lib $LDFLAGS"

    export CPPFLAGS="-I/usr/local/opt/openssl@1.1/include $CPPFLAGS"
    export LDFLAGS="-L/usr/local/opt/openssl@1.1/lib $LDFLAGS"
    export PKG_CONFIG_PATH="/usr/local/opt/openssl@1.1/lib/pkgconfig:$PKG_CONFIG_PATH"

    export CPPFLAGS="-I/usr/local/opt/readline/include $CPPFLAGS"
    export LDFLAGS="-L/usr/local/opt/readline/lib $LDFLAGS"

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
exec \"\${0%/*}\"/python$VERSION \"\$@\""
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
exec \"\${0%/*}\"/python$VERSION \"\$@\""
    ;;
esac
# Missing realpath on old operating systems
realpath --version || WRAPPER=$(echo "$WRAPPER" | sed -e "s/realpath/readlink -e/")

CONFIGURE="./configure --prefix="$PWD/install" --enable-ipv6 --enable-shared"
# Enable link time optimizations (LTO) except old gcc
[ "$(gcc --version 2>&1 | grep "gcc .* [1-4][.]")" ] || CONFIGURE="$CONFIGURE --with-lto"
# Check UCS4: sys.maxunicode = 1114111
CONFIGURE="$CONFIGURE --enable-unicode=ucs4"

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

    # Fix pip
    ##[ ! -f get-pip.py ] && wget https://bootstrap.pypa.io/pip/$VERSION/get-pip.py
    ##cat get-pip.py | install/bin/python$MAJOR_VER
    install/bin/python$MAJOR_VER -m ensurepip

    # Make relocatable scripts
    IFS=$'\n'
    for FILE in $(grep "^#!/.*[/ ]python" install/bin/* 2> /dev/null | grep -v ":#!/usr/bin/env python$MAJOR_VER" | sed -e "s@:#!/.*@@")
    do
         echo "$FILE: #!/usr/bin/env python$MAJOR_VER}"
         sed -i "s@^#!/.*python@#!/usr/bin/env python$MAJOR_VER@" "$FILE"
    done
    unset IFS

    # Fix for porting on Ubuntu and running on RHEL
    [ "$(uname)" = Linux ] && sed -i "s/libbz2.so.1.0/libbz2.so.1\x00\x00/" install/lib/python*/lib-dynload/*bz2*.so

    # Remove tests
    find install/lib/python* -type f -name '*test*.py' | grep "/[^/]*test[^/]*/" | sed -e "s/\/[^\/]*$//" | uniq | xargs rm -rf
fi

ls -ld install/bin/python* install/lib/libpython*
