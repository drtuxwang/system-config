#!/usr/bin/env bash
#
# Install/check Python packages requirements
#

set -u

# Process options
help() {
    echo "Usage: $0 [-pip|-i] <python-executable> [<requirement-file>]"
    exit 1
}
MODE=
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
        MODE="check"
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

esc=$'\033'
export PYTHONPATH=


read_requirements() {
    if [ -f "$1" ]
    then
        echo -e "${esc}[34mProcessing \"$1\"...${esc}[0m"
        for PACKAGE in $(sed -e "s/#.*//" "$1")
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
    PACKAGES=$($LIST | awk 'NR>=3 {printf("%s==%s\n", $1, $2)}')
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

    [ "$ERROR" ] && echo -e "${esc}[31mERROR!${esc}[0m" && exit 1
}


install_packages() {
    MODE=${1:-}
    case $PYTHON_VERSION in
    2.[67]|3.[3456])
        GETPIP="https://bootstrap.pypa.io/pip/$PYTHON_VERSION/get-pip.py"
        ;;
    *)
        GETPIP="https://bootstrap.pypa.io/pip/get-pip.py"
        ;;
    esac
    if [ ! "$($PYTHON -m pip --version 2>&1 | grep "^pip ")" ]
    then
        echo "curl --location --progress-bar $GETPIP | $PYTHON"
        curl --location --progress-bar $GETPIP | $PYTHON 2>&1 | grep -v "'root' user"
        [ ${PIPESTATUS[0]} = 0 ] || exit 1
        echo -e "${esc}[33mInstalled!${esc}[0m"
    fi

    PACKAGES=$(check_packages | grep -v "not found" | awk '/ # Requirement / {print $NF}')
    for PACKAGE in $(echo "$PACKAGES" | grep -E "^(pip|setuptools|wheel)([>=]=.*|)$")
    do
        echo "$INSTALL $PACKAGE"
        $INSTALL "$PACKAGE" 2>&1 | grep -v "'root' user"
        [ ${PIPESTATUS[0]} = 0 ] || exit 1
        echo -e "${esc}[33mInstalled!${esc}[0m"
    done
    [ "$MODE" = "piponly" ] && return

    export CRYPTOGRAPHY_DONT_BUILD_RUST=1
    for PACKAGE in $(echo "$PACKAGES" | grep -E -v "^(pip|setuptools|wheel)([>=]=.*|)$")
    do
        echo "$INSTALL $PACKAGE"
        $INSTALL "$PACKAGE" 2>&1 | grep -v "'root' user"
        [ ${PIPESTATUS[0]} = 0 ] || continue
        echo -e "${esc}[33minstalled!${esc}[0m"
    done
}


umask 022
LIST="$PYTHON -m pip list --no-python-version-warning --disable-pip-version-check"
INSTALL="$PYTHON -m pip install --no-python-version-warning --disable-pip-version-check --no-warn-script-location --no-deps"
[ -w "$($PYTHON -help 2>&1 | grep usage: | awk '{print $2}')" ] || INSTALL="$INSTALL --user"

PY_EXE=$(echo "import sys; print(sys.executable)" | $PYTHON 2> /dev/null)
PY_INC=$($PY_EXE-config --includes 2> /dev/null)  # "Python.h" etc
if [ "$(uname)" = Darwin ]
then
    # Homebrew
    export CPPFLAGS="-I/usr/local/opt/openssl@1.1/include $PY_INC ${CPPFLAGS:-}"
    export PKG_CONFIG_PATH="/usr/local/opt/openssl/lib/pkgconfig:/usr/local/opt/zlib/lib/pkgconfig"
else
    export CFLAGS="$PY_INC ${CFLAGS:-}"
fi

declare -A requirements
PYTHON_VERSION=$($PYTHON --version 2>&1 | awk '/^Python [1-9]/{print $2}' | cut -f1-2 -d.)
if [ "$REQUIREMENT" ]
then
    read_requirements "$REQUIREMENT"
else
    read_requirements "${0%/*}/python-requirements.txt"
    read_requirements "${0%/*}/python-requirements_${PYTHON_VERSION}.txt"
    case $(uname) in
    Darwin)
        read_requirements "${0%/*}/python-requirements_mac.txt"
        read_requirements "${0%/*}/python-requirements_${PYTHON_VERSION}mac.txt"
        ;;
    esac
fi

[ "$MODE" != check ] && install_packages "$MODE" && install_packages "$MODE"  # Retry
[ "$MODE" != piponly ] && check_packages
echo -e "${esc}[33mOK!${esc}[0m"
