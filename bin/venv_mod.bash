#!/usr/bin/env bash
#
# Bash Python Virtual Environments module
# - Build and run Python virtual environment
#
# Copyright GPL v2: 2023-2024 By Dr Colin Kong
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
    if [ ! -d "$VIRTUAL_ENV" ]
    then
        $VENV_PYTHON -m virtualenv "$VIRTUAL_ENV" || exit 1
        rm -f "$VIRTUAL_ENV/.gitignore"
    fi

    "$VIRTUAL_ENV/bin/$VENV_PYTHON" -m pip install $VENV_PACKAGE $VENV_DEPENDS || exit 1
    [ "VENV_CLEAN" != "yes" ] && find "$VIRTUAL_ENV/lib" -type f -name '*test*.py' | grep "/[^/]*test[^/]*/" | sed -e "s/\/[^\/]*$//" | uniq | xargs rm -rfv
    IFS=$'\n'
    for FILE in $(grep "^#!/.*/python" "$VIRTUAL_ENV/bin"/* 2> /dev/null | grep -v ":#!/usr/bin/env " | sed -e "s@:#!/.*@@")
    do
        echo "$FILE: #!/usr/bin/env $VENV_PYTHON"
        sed -i "s@^#!/.*@#!/usr/bin/env $VENV_PYTHON@" "$FILE"
    done
    unset IFS

    $VENV_POSTINST
}


# Show Virtual Environment configurations
[ "${0##*/}" = venv_mod.bash ] && show_virtualenvs && exit

# Setup Virtual Environment
defaults_settings
virtualenv_setup

PYTHON_DIR=$(echo "import sys; print(sys.exec_prefix)" | "$VENV_PYTHON")
VIRTUAL_ENV="$PYTHON_DIR-venv/${VENV_PACKAGE/==/-}"
[ -d "$VIRTUAL_ENV" ] || [ -w "${VIRTUAL_ENV%/*/*}" ] || VIRTUAL_ENV="${TMPDIR:-/tmp/$(id -un)}/$($VENV_PYTHON --version 2>&1 | sed -e "s/ /-/g")-venv/${VENV_PACKAGE/==/-}"
FLAGS="${1:-}"
export VIRTUAL_ENV
export PATH="$VIRTUAL_ENV/bin:$PATH"
[ "$("$VIRTUAL_ENV/bin/$VENV_PYTHON" -m pip freeze 2> /dev/null | grep -i "^$VENV_PACKAGE$")" ] || create_virtualenv "$@"

$VENV_PRERUN
[[ ${0##*/} =~ venv-* ]] && echo -e "\nVIRTUAL_ENV=$VIRTUAL_ENV" && exec bash -l
exec "${0##*/}" "$@"
