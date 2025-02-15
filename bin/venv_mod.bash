#!/usr/bin/env bash
#
# Bash Python Virtual Environments module
# - Build and run Python virtual environment
#
# Copyright GPL v2: 2023-2025 By Dr Colin Kong
#

set -u


defaults_settings() {
    VENV_PYTHON=
    VENV_PACKAGE=
    VENV_DEPENDS=
    VENV_CLEAN=yes
    VENV_POSTINST=
    VENV_PRERUN=
}

show_virtualenvs() {
    for FILE in "${0%/*}"/venv-*
    do
        echo "${FILE##*/}" | awk '{printf("%-24s", $1)}'
        grep -E "VENV_(PYTHON=|PACKAGE=|source )" "$FILE" | grep -v "/${0##*/}" | sed -e 's/  *#.*//;s@^[^=]*[=/]@@;s/"//g' | awk '{printf(" %s", $NF)}'
        echo
    done
}

create_virtualenv() {
    echo -e "\033[33mCreating Python VirtualEnv: $VIRTUAL_ENV\033[0m"
    umask 022

    VERSION=$($VENV_PYTHON --version 2>&1 | awk '/^Python [1-9]/{print $2}')
    case $(uname) in
    Darwin)
        WRAPPER="#!/usr/bin/env bash

PYTHON_LIB=\$(realpath \"\${0%/*}/python$VERSION\" | sed -e \"s,bin/[^/]*$,lib,\")
export DYLD_LIBRARY_PATH=\"\$PYTHON_LIB:\$DYLD_LIBRARY_PATH\"
export LDFLAGS=\"-L\$PYTHON_LIB\"
exec \"\${0%/*}/python$VERSION\" \"\$@\""
        ;;
    *)
        WRAPPER="#!/usr/bin/env bash

PYTHON_LIB=\$(realpath \"\${0%/*}/python$VERSION\" | sed -e \"s,bin/[^/]*$,lib,\")
export LD_LIBRARY_PATH=\"\$PYTHON_LIB:\$LD_LIBRARY_PATH\"
export LDFLAGS=\"-L\$PYTHON_LIB\"
exec \"\${0%/*}/python$VERSION\" \"\$@\""
        ;;
    esac

    if [ ! -d "$VIRTUAL_ENV" ]
    then
        rm -rf "$VIRTUAL_ENV.part"
        $VENV_PYTHON -m virtualenv "$VIRTUAL_ENV.part" || exit 1
        rm -f "$VIRTUAL_ENV.part/.gitignore"
    fi

    rm -f "$VIRTUAL_ENV.part/bin"/python$VERSION "$VIRTUAL_ENV.part/bin"/python${VERSION%%.*} "$VIRTUAL_ENV.part/bin"/python${VERSION%.*}
    mv "$VIRTUAL_ENV.part/bin/python" "$VIRTUAL_ENV.part/bin"/python$VERSION
    echo "$WRAPPER" > "$VIRTUAL_ENV.part/bin"/python${VERSION%.*}
    chmod 755 "$VIRTUAL_ENV.part/bin"/python${VERSION%.*}
    ln -s python${VERSION%.*} "$VIRTUAL_ENV.part/bin"/python${VERSION%%.*}
    ln -s python${VERSION%.*} "$VIRTUAL_ENV.part/bin"/python

    for VENV_DEPEND in $VENV_DEPENDS
    do
          "$VIRTUAL_ENV.part/bin/$VENV_PYTHON" -m pip install $VENV_DEPEND || exit 1
    done
    "$VIRTUAL_ENV.part/bin/$VENV_PYTHON" -m pip install $VENV_PACKAGE || exit 1
    [ "$VENV_CLEAN" = "yes" ] && find "$VIRTUAL_ENV.part/lib" -type f -name '*test*.py' | grep "/[^/]*test[^/]*/" | sed -e "s/\/[^\/]*$//" | uniq | xargs rm -rfv
    IFS=$'\n'
    for FILE in $(
        grep "^#!/.*/python" "$VIRTUAL_ENV.part/bin"/* 2> /dev/null | grep -v ":#!/usr/bin/env " | sed -e "s@:#!/.*@@";
        grep "'''exec'.*bin/python" "$VIRTUAL_ENV.part/bin"/* 2> /dev/null | sed -e "s/:'''.*//"
    )
    do
        echo "$FILE: #!/usr/bin/env $VENV_PYTHON"
        sed -i "s@^#!/.*@#!/usr/bin/env $VENV_PYTHON@" "$FILE"
    done
    unset IFS
    [[ $VERSION =~ 2.* ]] && cp -p $PYTHON_DIR/lib/libpython*.so.* $VIRTUAL_ENV.part/lib 2> /dev/null

    VIRTUAL_ENV=$VIRTUAL_ENV.part $VENV_POSTINST

    mv $VIRTUAL_ENV.part $VIRTUAL_ENV
}


# Show Virtual Environment configurations
[ "${0##*/}" = venv_mod.bash ] && show_virtualenvs && exit

# Setup Virtual Environment
defaults_settings
virtualenv_setup

PYTHON_DIR=$(echo "import sys; print(sys.exec_prefix)" | "$VENV_PYTHON")
VENV_PACKAGE=${VENV_PACKAGE,,}
VIRTUAL_ENV="$PYTHON_DIR-venv/${VENV_PACKAGE/==/_}"
[ -d "$VIRTUAL_ENV" ] || [ -w "${VIRTUAL_ENV%/*/*}" ] || VIRTUAL_ENV="${TMPDIR:-/tmp/$(id -un)}/python-$($VENV_PYTHON --version 2>&1 | awk '/^Python [1-9]/{print $2}')-venv/${VENV_PACKAGE/==/_}"
FLAGS="${1:-}"
export VIRTUAL_ENV
export PATH="$VIRTUAL_ENV/bin:$PATH"
[ "$("$VIRTUAL_ENV/bin/$VENV_PYTHON" -m pip freeze 2> /dev/null | grep -i "^$VENV_PACKAGE$")" ] || create_virtualenv "$@"

$VENV_PRERUN
[[ ${0##*/} =~ venv-* ]] && echo -e "\nVIRTUAL_ENV=$VIRTUAL_ENV" && exec bash -l
exec "${0##*/}" "$@"
