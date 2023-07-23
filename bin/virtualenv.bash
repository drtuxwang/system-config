#!/usr/bin/env bash
#
# Build Python virtual environment
# (set PYTHON, PACKAGE, DEPENDS, POSTINST)
#

set -u


create_virtualenv() {
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


# Setup Virtual Environment
PYTHON_DIR=$(echo "import sys; print(sys.exec_prefix)" | "$PYTHON")
VIRTUAL_ENV="$PYTHON_DIR-venv/${PACKAGE/==/-}"
[ -d "$VIRTUAL_ENV" ] || [ -w "${VIRTUAL_ENV%/*/*}" ] || VIRTUAL_ENV="$TMP/$($PYTHON --version 2>&1 | sed -e "s/ /-/g")-venv/${PACKAGE/==/-}"
FLAGS="${1:-}"
export VIRTUAL_ENV
export PATH="$VIRTUAL_ENV/bin:$PATH"
[ "$("$VIRTUAL_ENV/bin/$PYTHON" -m pip freeze 2> /dev/null | grep -i "^$PACKAGE$")" ] || create_virtualenv "$@"

[ "${0##*-}" = venv ] && exec bash -l
