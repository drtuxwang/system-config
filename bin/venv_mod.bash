#!/usr/bin/env bash
#
# Bash Python Virtual Environments module
#
# Build and run Python virtual environment (set PYTHON, PACKAGE, DEPENDS, POSTINST)
#
# Copyright GPL v2: 2023-2024 By Dr Colin Kong
#

set -u


create_virtualenv() {
    echo -e "\033[33mCreating Python VirtualEnv: $VIRTUAL_ENV\033[0m"
    umask 022
    if [ ! -d "$VIRTUAL_ENV" ]
    then
        $PYTHON -m virtualenv "$VIRTUAL_ENV" || exit 1
        rm -f "$VIRTUAL_ENV/.gitignore"
        if [ -h "$VIRTUAL_ENV/bin/python" ]
        then
            ln -sf "$PYTHON_DIR/bin/$PYTHON" "$VIRTUAL_ENV/bin/$PYTHON"
            ln -sf "$PYTHON" "$VIRTUAL_ENV/bin/${PYTHON%.*}"
            rm -f "$VIRTUAL_ENV/bin/"python
        fi
    fi

    "$VIRTUAL_ENV/bin/$PYTHON" -m pip install $PACKAGE $DEPENDS || exit 1
    [ "${1:-}" != "-noclean" ] && find "$VIRTUAL_ENV/lib" -type f -name '*test*.py' | grep "/[^/]*test[^/]*/" | sed -e "s/\/[^\/]*$//" | uniq | xargs rm -rfv
    IFS=$'\n'
    for FILE in $(grep "^#!/.*/python" "$VIRTUAL_ENV/bin"/* 2> /dev/null | grep -v ":#!/usr/bin/env " | sed -e "s@:#!/.*@@")
    do
        echo "$FILE: #!/usr/bin/env $PYTHON"
        sed -i "s@^#!/.*@#!/usr/bin/env $PYTHON@" "$FILE"
    done
    unset IFS

    $POSTINST
}


# Show Virtual Environment configurations
if [ "${0##*/}" = venv_mod.bash ]
then
    for FILE in "${0%/*}"/venv-*
    do
        echo "${FILE##*/}" | awk '{printf("%-24s", $1)}'
        grep -E "(PYTHON=|PACKAGE=|source )" "$FILE" | grep -v "/${0##*/}" | sed -e 's/  *#.*//;s@^[^=]*[=/]@@;s/"//g' | awk '{printf(" %s", $NF)}'
        echo
    done
    exit
fi

# Setup Virtual Environment
PYTHON_DIR=$(echo "import sys; print(sys.exec_prefix)" | "$PYTHON")
VIRTUAL_ENV="$PYTHON_DIR-venv/${PACKAGE/==/-}"
[ -d "$VIRTUAL_ENV" ] || [ -w "${VIRTUAL_ENV%/*/*}" ] || VIRTUAL_ENV="${TMPDIR:-/tmp/$(id -un)}/$($PYTHON --version 2>&1 | sed -e "s/ /-/g")-venv/${PACKAGE/==/-}"
FLAGS="${1:-}"
export VIRTUAL_ENV
export PATH="$VIRTUAL_ENV/bin:$PATH"
[ "$("$VIRTUAL_ENV/bin/$PYTHON" -m pip freeze 2> /dev/null | grep -i "^$PACKAGE$")" ] || create_virtualenv "$@"

[[ ${0##*/} =~ venv-* ]] && echo -e "\nVIRTUAL_ENV=$VIRTUAL_ENV" && exec bash -l
