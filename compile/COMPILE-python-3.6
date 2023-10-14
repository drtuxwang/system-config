#!/usr/bin/env bash

VERSION="3.6"

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
    ;;
*)
    if [[ ${0%/*} =~ ^COMPILE32 ]]
    then
        export CPPFLAGS="-m32"
        export CFLAGS="-m32"
        export LDFLAGS="-m32"
    fi
    ;;
esac

# Fix pip Segmentation fault
sed -i "s/double dummy;/long double dummy;/" Include/objimpl.h
sed -i "s/#define ALIGNMENT               8/#define ALIGNMENT               16/" Objects/obmalloc.c
sed -i "s/#define ALIGNMENT_SHIFT         3/#define ALIGNMENT_SHIFT         4/" Objects/obmalloc.c

umask 022
./configure --prefix="$PWD/install"
make
make install

# Fix pip (https://bootstrap.pypa.io/pip/$VERSION/get-pip.py)
install/bin/python$VERSION get-pip.py

if [ -d install/bin ]
then
    for FILE in $(cd install/bin; ls -1 | grep -v "*.py$")
    do
        if [ "$(grep "^#!/.*/python$VERSION" "install/bin/$FILE")" ]
        then
            PYFILE=$(echo "$FILE.py" | sed -e "s/-$VERSION//" -e "s/[.][1-9][0-9]*m*//")
            sed -e "1s@^#.*@#!/usr/bin/env python$VERSION@" "install/bin/$FILE" > "install/bin/$PYFILE"
            rm -f "install/bin/$FILE"
            echo "#!/usr/bin/env bash
MYDIR=\${0%/*}
exec \"\$MYDIR/python$VERSION\" \"\$MYDIR/$PYFILE\" \"\$@\"" > "install/bin/$FILE"
            chmod 755 "install/bin/$FILE"
        fi
    done

    if [ -x "install/bin/python${VERSION}m" ]
    then
        ln -sf "python$VERSION" "install/bin/python${VERSION}m"
        mv "install/bin/python${VERSION}m-config" "install/bin/python${VERSION}-config"
        ln -s "python${VERSION}-config" "install/bin/python${VERSION}m-config"

        IFS=$'\n'
        for FILE in $(grep "^#!/.*[/ ]python" install/bin/* 2> /dev/null | grep -v ":#!/usr/bin/env python$VERSION" | sed -e "s@:#!/.*@@")
        do
            echo "$FILE: #!/usr/bin/env python$VERSION}"
            sed -i "s@^#!/.*python@#!/usr/bin/env python$VERSION@" "$FILE"
        done
        unset IFS
    fi

    sed -e "s@^prefix_build=.*@prefix_build=\${0%/*/*}@" -e "s@\".*/install/lib@\"\$prefix_build/lib@" \
        "install/bin/python$VERSION-config" > "install/bin/python$VERSION-config-new"
    mv "install/bin/python$VERSION-config-new" "install/bin/python$VERSION-config"
    chmod 755 "install/bin/python$VERSION-config"

    # Fix readonly permission on some libraries
    chmod -R u+w install

    # Fix for porting on Ubuntu and running on RHEL
    [ "$(uname)" = Linux ] && sed -i "s/libbz2.so.1.0/libbz2.so.1\x00\x00/" install/lib/python*/lib-dynload/*bz2*.so

    # Remove tests
    find install/lib/python* -type f -name '*test*.py' | grep "/[^/]*test[^/]*/" | sed -e "s/\/[^\/]*$//" | uniq | xargs rm -rf

    rm install/bin/python3
fi

ls -ld install/* install/bin/*
