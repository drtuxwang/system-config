#!/usr/bin/env bash
#
# Install/check Python packages requirements
#

set -u

# Process options
help() {
    echo "Usage: $0 [-pip|-i|-c|-u] <python-executable> [<requirement-file>]"
    exit 1
}
MODE=install
while [ $# != 0 ]
do
    case $1 in
    -pip)
        MODE="piponly"
        ;;
    -i)
        MODE="install"
        ;;
    -c)
        MODE="checkonly"
        ;;
    -u)
        MODE="uninstall"
        ;;
    -*)
        help
        ;;
    *)
        break
        ;;
    esac
    shift
done
PYTHON=${1-}
REQUIREMENT=${2-}
[[ ! /$PYTHON =~ /python[1-9]* ]] && help

export PYTHONPATH=
export PIP_BREAK_SYSTEM_PACKAGES=1  # Fix >= 3.11


get_pip() {
    case $MAJOR_VER in
    2.[67]|3.[3456])
        GETPIP="https://bootstrap.pypa.io/pip/$MAJOR_VER/get-pip.py"
        ;;
    *)
        GETPIP="https://bootstrap.pypa.io/pip/get-pip.py"
        ;;
    esac
    echo "curl --location --progress-bar $GETPIP | $PYTHON"
    curl --location --progress-bar $GETPIP | $PYTHON 2>&1 | grep -v "'root' user"
    return ${PIPESTATUS[0]}
}

pip_list() {
    $PIP_LIST "$@" 2> /dev/null | awk 'NR>=3 {printf("%s==%s\n", $1, $2)}' | sed -e "s/_/-/g"
    return ${PIPESTATUS[0]}
}

pip_install() {
    $PIP_INSTALL "$@" --no-deps 2>&1 | grep -Ev "'root' user|pip version|consider upgrading"
    return ${PIPESTATUS[0]}
}

pip_uninstall() {
    $PIP_UNINSTALL "$@" 2>&1 | grep -v "'root' user"
    return ${PIPESTATUS[0]}
}

read_requirements() {
    if [ -f "$1" ]
    then
        echo -e "\033[34mProcessing \"$1\"...\033[0m"
        for PACKAGE in $(sed -e "s/ *# ==/==/;s/#.*//;s/ .*//" "$1")
        do
            NAME=${PACKAGE%==*}
            if [[ ! $PACKAGE =~ ==None$ ]]
            then
                requirements[$NAME]="$PACKAGE"
            else
                unset requirements[$NAME]
            fi
        done
    fi
}


check_packages() {
    ERROR=
    PACKAGES=$(pip_list)
    for PACKAGE in $PACKAGES
    do
        NAME=${PACKAGE%==*}
        if [ -v requirements[$NAME] ]
        then
            REQUIRED=${requirements[$NAME]}
            if [ "$REQUIRED" != "$PACKAGE" -a "$(echo "$REQUIRED" |grep "[>=]=")" ]
            then
                echo $PACKAGE $REQUIRED | awk '{printf("%-27s  # Requirement %s\n", $1, $2)}'
                ERROR=1
            fi
        elif [ "$MODE" = "uninstall" ]
        then
            echo y | pip_uninstall $PACKAGE
            echo -e "\033[33mUninstalled!\033[0m"
        else
            echo $PACKAGE | awk '{printf("%-27s  # Requirement not found\n", $1)}'
        fi
    done
    for PACKAGE in ${requirements[@]}
    do
        if [ ! "$(echo "$PACKAGES" | grep "^${PACKAGE%[>=]=*}==")" ]
        then
            echo "                      # Requirement $PACKAGE"
            ERROR=1
        fi
    done

    for DIR in $($PYTHON -m site | grep site-packages | cut -f2 -d"'")
    do
        for FILE in $(awk '/^[^_]/ {print $1}' $DIR/*.dist-info/top_level.txt 2> /dev/null | grep -v "^DUMMY$")
        do
            case $FILE in
            pvectorc)  # Ignore missing
                ;;
            *)
                if [ ! "$(ls $DIR/$FILE $DIR/$FILE.* 2> /dev/null)" ]
                then
                    grep $FILE $DIR/*.dist-info/top_level.txt | \
                    ERROR=1
                fi
                ;;
            esac
        done
    done
    $PYTHON -m pip check 2>&1 | grep -Ev "DEPRECATION:|No broken requirements"
    [ ${PIPESTATUS[0]} = 0 ] || ERROR=1

    [ "$ERROR" ] && echo -e "\033[31mERROR!\033[0m" && exit 1
}


install_packages() {
    MODE=${1:-}
    if [ ! "$($PYTHON -m pip --version 2>&1 | grep "^pip ")" ]
    then
        get_pip || exit 1
        echo -e "\033[33mInstalled!\033[0m"
    fi

    PACKAGES=$(check_packages | grep -v "not found" | awk '/ # Requirement / {print $NF}')
    for PACKAGE in $(echo "$PACKAGES" | grep -E "^(pip|setuptools|wheel)([>=]=.*|)$")
    do
        echo -e "\033[33mInstalling package \"$PACKAGE\"...\033[0m"
        pip_install "$PACKAGE" || exit 1
        echo -e "\033[33mInstalled!\033[0m"
    done
    [ "$MODE" = "piponly" ] && return

    export CRYPTOGRAPHY_DONT_BUILD_RUST=1
    for PACKAGE in $(echo "$PACKAGES" | grep -E -v "^(pip|setuptools|wheel)([>=]=.*|)$")
    do
        echo -e "\033[33mInstalling package \"$PACKAGE\"...\033[0m"
        pip_install "$PACKAGE" || continue
        echo -e "\033[33minstalled!\033[0m"
    done

    PYTHON_DIR=$(echo "import sys; print(sys.exec_prefix)" | "$PYTHON")
    find "$PYTHON_DIR/lib"/python* -type f -name '*test*.py' | grep "/[^/]*test[^/]*/" | sed -e "s/\/[^\/]*$//" | uniq | xargs rm -rfv
    find "$PYTHON_DIR"/*doc* -type d 2> /dev/null | xargs rm -rfv

    if [ -w "$PY_EXE" ]
    then
        IFS=$'\n'
        for FILE in $(grep "^#!/.*[/ ]python" ${PY_EXE%/*}/* 2> /dev/null | grep -v ":#!/usr/bin/env python$MAJOR_VER" | sed -e "s@:#!/.*@@")
        do
            echo "$FILE: #!/usr/bin/env python$MAJOR_VER"
            sed -i "s@^#!/.*[/ ]python.*@#!/usr/bin/env python$MAJOR_VER@" "$FILE"
        done
        unset IFS
    fi
}


umask 022

MAJOR_VER=$($PYTHON --version 2>&1 | awk '/^Python [1-9]/{print $2}' | cut -f1-2 -d.)
PY_EXE=$(echo "import sys; print(sys.executable)" | $PYTHON 2> /dev/null)
PY_INC=$($PY_EXE-config --includes 2> /dev/null)  # "Python.h" etc
PIP_LIST="$PYTHON -m pip list"
PIP_INSTALL="$PYTHON -m pip install"
PIP_UNINSTALL="$PYTHON -m pip uninstall"
[ -w "$($PYTHON -help 2>&1 | grep usage: | awk '{print $2}')" ] || PIP_INSTALL="$PIP_INSTALL --user"

if [ "$(uname)" = Darwin ]
then
    # Homebrew
    export CPPFLAGS="-I/usr/local/opt/openssl@1.1/include $PY_INC ${CPPFLAGS:-}"
    export PKG_CONFIG_PATH="/usr/local/opt/openssl/lib/pkgconfig:/usr/local/opt/zlib/lib/pkgconfig"
else
    export CFLAGS="$PY_INC ${CFLAGS:-}"
fi
echo -e "\033[33mChecking \"$PY_EXE\"...\033[0m"

declare -A requirements
if [ "$REQUIREMENT" ]
then
    read_requirements "$REQUIREMENT"
else
    read_requirements "${0%/*}/python-requirements.txt"
    read_requirements "${0%/*}/python-requirements_$MAJOR_VER.txt"
    case $(uname) in
    Darwin)
        read_requirements "${0%/*}/python-requirements_mac.txt"
        read_requirements "${0%/*}/python-requirements_${MAJOR_VER}mac.txt"
        ;;
    esac
fi

[ "$MODE" = install -o "$MODE" = piponly ] && install_packages "$MODE" && install_packages "$MODE"  # Retry
[ "$MODE" != piponly ] && check_packages
echo -e "\033[33mOK!\033[0m"
