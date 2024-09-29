#!/usr/env/bin bash
#
# Bash Python launcher module
#
# Python loader for starting system/non system Python or Python tools/modules
#
# Copyright GPL v2: 2006-2024 By Dr Colin Kong
#


#
# Function to redirect Python dot files/directories to temp cache
#
temp_dotfiles() {
    MYUNAME=$(id -un)
    mkdir -p /tmp/$MYUNAME/.cache
    chmod 700 /tmp/$MYUNAME
    if [ "$HOME" -a ! -h $HOME/.python_history ]
    then
         rm -f $HOME/.python_history
         ln -s /tmp/$MYUNAME/.cache/python_history $HOME/.python_history 2> /dev/null
    fi

    case "${0##*/} $@ " in
    ansible|ansible[\ -]*)
        mkdir -p /tmp/$MYUNAME/.cache/ansible
        if [ ! -h $HOME/.ansible ]
        then
            rm -rf $HOME/.ansible
            ln -s /tmp/$MYUNAME/.cache/ansible $HOME/.ansible
        fi
        ;;
    esac
}

#
# Function to locate Python command
#
locate_python() {
    if [ "$VIRTUAL_ENV" -a -x "$VIRTUAL_ENV/bin/$PYLD_EXE" ]
    then
        echo "$VIRTUAL_ENV/bin/$PYLD_EXE"
        return
    fi

    case $0 in
    /*)
        LOCAL=${0%/*/*}
        ;;
    ?*)
        LOCAL="$(pwd)/${0%/*}/.."
        ;;
    esac

    LOCATE=$(ls -1t $LOCAL/*/bin/$PYLD_EXE 2> /dev/null | head -1)
    if [ "$LOCATE" ]
    then  # Create "$LOCAL/*/bin/python3" wrapper script to pick system Python
        echo "$LOCATE"
        return
    fi

    case $(uname) in
    Darwin)
        case $(uname -m) in
        i386|x86_64)
            if [ "$(/usr/sbin/sysctl -a | grep "hw.cpu64bit_capable: 1$")" ]
            then
                LOCATE=$(ls -1t $LOCAL/*/macos64_*-x86*/bin/$PYLD_EXE 2> /dev/null | head -1)
            fi
        esac
        ;;
    Linux)
        GLIBC=$(ldd /bin/sh | grep libc | sed -e "s/.*=>//" | awk '{print $1}')
        GLIBC_VER=$(strings "$GLIBC" 2> /dev/null | grep 'GNU C Library' | head -1 | sed -e 's/.*version//;s/,//;s/[.]$//' | awk '{print $1}')
        case $(uname -m) in
        x86_64)
            LOCATE=$((ls -1t $LOCAL/*/*linux64_*-x86*glibc_$GLIBC_VER/bin/$PYLD_EXE; ls -1t $LOCAL/*/linux64_*-x86*/bin/$PYLD_EXE) 2> /dev/null | head -1)
            ;;
        i*86)
            LOCATE=$((ls -1t $LOCAL/*/*linux_*-x86*glibc_$GLIBC_VER/bin/$PYLD_EXE; ls -1t $LOCAL/*/linux_*-x86*/bin/$PYLD_EXE) 2> /dev/null | head -1)
            ;;
        ppc*)
            LOCATE=$((ls -1t $LOCAL/*/*linux_*-power*$GLIBC_VER/bin/$PYLD_EXE; ls -1t $LOCAL/*/linux_*-power*/bin/$PYLD_EXE) 2> /dev/null | head -1)
            ;;
        sparc*)
            LOCATE=$((ls -1t $LOCAL/*/*linux_*-sparc*$GLIBC_VER/bin/$PYLD_EXE; ls -1t $LOCAL/*/linux_*-sparc*/bin/$PYLD_EXE) 2> /dev/null | head -1)
            ;;
        esac
        if [ ! "$LOCATE" ]
        then
            case $(uname -m) in
            ia64|x86_64)
                LOCATE=$(ls -1t $LOCAL/*/*linux_*-x86*/bin/$PYLD_EXE 2> /dev/null | head -1)
                ;;
            esac
        fi
        ;;
    *NT*)
        export PYTHONUTF8=1  # Python 3.7+ UTF-8 files
        PYLD_EXE="$PYLD_EXE.exe"
        if  [ "$PROCESSOR_ARCHITEW6432" = AMD64 ]
        then
            LOCATE=$(ls -1t $LOCAL/*/*windows64_*-x86*/$PYLD_EXE 2> /dev/null | head -1)
        fi
        if [ ! "$LOCATE" ]
        then
            LOCATE=$(ls -1t $LOCAL/*/*windows_*-x86*/$PYLD_EXE 2> /dev/null | head -1)
        fi
        ;;
    esac

    echo "$LOCATE"
}

#
# Function to return location of program
#
which() {
    PATH=$(echo ":$PATH:" | sed -e "s@:${0%/*}:@:@;s/^://;s/:$//")

    IFS=:
    for CDIR in $PATH
    do
        CMD="$CDIR/$1"
        if [ -x "$CMD" -a ! -d "$CMD" ]
        then
            echo "$CMD" | sed -e "s@//*@/@g"; return
        fi
    done
    unset IFS
}

#
# Function to locate Python tool
#
locate_python_tool() {
    for TOOL in $HOME/.local/bin/$2 /usr/local/bin/$2 $1/$2 $1/Tools/scripts/$2 $1/Scripts/$2.exe
    do
        if [ -f "$TOOL.py" -a "${TOOL##*/}.py" != "pip3.py" ]  # pip3.py is broken
        then
            echo "$TOOL.py"
            return
        fi
        if [ -f "$TOOL" ]
        then
            echo "$TOOL"
            return
        fi
    done
}

#
# Execute Python or Python tool
#
exec_python() {
    export PYTHONDONTWRITEBYTECODE=1
    PYLD_BIN=${0%/*}
    if [ ! "$PYLD_EXE" ]
    then
        PYLD_EXE=python3
    fi
    if [ "$PYLD_MAIN" ]
    then
        PYLD_FLAGS="-pyldname=${0##*/}"
    else
        PYLD_MAIN="${0##*/}"
        PYLD_FLAGS=
    fi
    if [ "$PYTHON_VENVS" -a "$(echo "$PYLD_MAIN" | grep -E "^(${PYTHON_VENVS//[, ]/|})")" -a ! "$VIRTUAL_ENV" ]
    then
        [ -x "$PYLD_BIN/venv-${0##*/}" ] && source "$PYLD_BIN/venv-${0##*/}" "$@" && exit 1
        [ -x "$PYLD_BIN/venv-${PYLD_MAIN%-*}" ] && source "$PYLD_BIN/venv-${PYLD_MAIN%-*}" "$@" && exit 1
    fi

    if [ "$OSTYPE" = "cygwin" ]
    then
        ARGS=
        while [ $# -gt 0 ]
        do
            if [ -f "$1" ]
            then
                ARG=$(cygpath -w "$1" 2> /dev/null | sed -e "s/%/%25/g;s/ /%20/g")
            else
                ARG=$(echo "$1" | sed -e "s/%/%25/g;s/ /%20/g")
            fi
            if [ "$ARGS" ]
            then
                ARGS="$ARGS
    $ARG"
            else
                ARGS="$ARG"
            fi
            shift
        done
        for ARG in $ARGS
        do
            set -- "$@" "$(echo "$ARG" | sed -e 's/%20/ /g;s/%25/%/g')"
        done
    fi

    PYTHON=$(locate_python "$@")
    if [ ! "$PYTHON" ]
    then
        PYTHON=$(which $PYLD_EXE)
        if [ ! "$PYTHON" ]
        then
            LOCATE=$(which "${0##*/}")
            [ "$LOCATE" ] && exec "$LOCATE" "$@"
            echo "Error: Cannot locate python for \"${0##*/}\" software." 1>&2
            exit 1
        fi
    fi

    unset PYTHONSTARTUP PYTHONHOME

    if [ "$PYLD_EXE" = "$PYLD_MAIN" ]
    then
        exec $PYTHON "$@"
    fi

    if [ -f "$PYLD_BIN/$PYLD_MAIN.py" ]
    then
        exec "$PYTHON" -B -E "$PYLD_BIN/pyld_mod.py" $PYLD_FLAGS $PYLD_MAIN "$@"
    fi

    if [ "$PYLD_EXE" != "$PYLD_MAIN" ]
    then
        PYLD_BIN=${PYTHON%/*}
        TOOL=$(locate_python_tool "$PYLD_BIN" "$PYLD_MAIN")
        if [ "$TOOL" ]
        then
            case "$TOOL" in
            *.exe)
                exec $PYTHON $TOOL "$@"
                ;;
            esac
            if [ "$(head -1 "$TOOL" | grep '#!.*python')" ]
            then
                exec $PYTHON $TOOL "$@"
            fi
            exec $TOOL "$@"
        fi
    fi
    if [ ! "$(which "$PYLD_MAIN")" ]
    then
        echo "Error: Cannot find required \"$PYLD_MAIN\" software." 1>&2
    fi
    exec $(which "$PYLD_MAIN") "$@"
}


temp_dotfiles "$@"
exec_python "$@"
