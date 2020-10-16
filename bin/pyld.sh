#!/bin/sh
#
# Python loader for starting system/non system Python or Python tools/modules
#


#
# Function to redirect Python dot files/directories to cache
#
cache_dotfiles() {
    mkdir -p $HOME/.cache
    if [ ! -h $HOME/.pylint.d ]
    then
        rm -rf $HOME/.pylint.d
        ln -s $TMP/.cache $HOME/.pylint.d
    fi
    if [ ! -h $HOME/.python_history ]
    then
        rm -f $HOME/.python_history
        ln -s $TMP/.cache/python_history $HOME/.python_history
    fi
}


#
# Function to locate Python command
#
locate_python() {
    case $0 in
    /*)
        LOCAL=`dirname \`dirname "$0"\``
        ;;
    ?*)
        LOCAL="`pwd`/`dirname $0`/.."
        ;;
    esac

    LOCATE=`ls -1t $LOCAL/*/bin/$PYEXE 2> /dev/null | head -1`
    if [ "$LOCATE" ]
    then  # Create "$LOCAL/*/bin/python3" wrapper script to pick system Python
        echo "$LOCATE"
        return
    fi

    case `uname` in
    Darwin)
        case `uname -m` in
        i386|x86_64)
            if [ "`/usr/sbin/sysctl -a | grep \"hw.cpu64bit_capable: 1$\"`" ]
            then
                LOCATE=`ls -1t $LOCAL/*/macos64_*-x86*/bin/$PYEXE 2> /dev/null | head -1`
            fi
        esac
        ;;
    Linux)
        case `uname -m` in
        x86_64)
            LOCATE=`ls -1t $LOCAL/*/linux64_*-x86*/bin/$PYEXE 2> /dev/null | head -1`
            ;;
        i*86)
            LOCATE=`ls -1t $LOCAL/*/linux_*-x86*/bin/$PYEXE 2> /dev/null | head -1`
            ;;
        ppc*)
            LOCATE=`ls -1t $LOCAL/*/linux64_*-power*/bin/$PYEXE 2> /dev/null | head -1`
            ;;
        sparc*)
            LOCATE=`ls -1t $LOCAL/*/linux64_*-sparc*/bin/$PYEXE 2> /dev/null | head -1`
            ;;
        esac
        if [ ! "$LOCATE" ]
        then
            case `uname -m` in
            ia64|x86_64)
                LOCATE=`ls -1t $LOCAL/*/linux_*-x86*/bin/$PYEXE 2> /dev/null | head -1`
                ;;
            esac
        fi
        ;;
    SunOS)
        case `uname -m` in
        i86pc)
            if [ -d /lib/amd64 ]
            then
                LOCATE=`ls -1t $LOCAL/*/sunos64_*-x86*/bin/$PYEXE 2> /dev/null | head -1`
            fi
            if [ ! "$LOCATE" ]
            then
                LOCATE=`ls -1t $LOCAL/*/sunos_*-x86*/bin/$PYEXE 2> /dev/null | head -1`
            fi
            ;;
        *)
            LOCATE=`ls -1t $LOCAL/*/sunos64_*-sparc*/bin/$PYEXE 2> /dev/null | head -1`
            if [ ! "$LOCATE" ]
            then
                LOCATE=`ls -1t $LOCAL/*/sunos_*-sparc*/bin/$PYEXE 2> /dev/null | head -1`
            fi
            ;;
        esac
        ;;
    *NT*)
        PYEXE="$PYEXE.exe"
        if  [ "$PROCESSOR_ARCHITEW6432" = AMD64 ]
        then
            LOCATE=`ls -1t $LOCAL/*/windows64_*-x86*/$PYEXE 2> /dev/null | head -1`
        fi
        if [ ! "$LOCATE" ]
        then
            LOCATE=`ls -1t $LOCAL/*/windows_*-x86*/$PYEXE 2> /dev/null | head -1`
        fi
        ;;
    esac

    echo "$LOCATE"
}


#
# Function to return location of program
#
which() {
    PATH=`echo ":$PATH:" | sed -e "s@:\`dirname \"$0\"\`:@:@"`

    for CDIR in `echo $PATH | sed -e "s/ /%20/g;s/:/ /g"`
    do
        CMD=`echo "$CDIR/$1" | sed -e "s/%20/ /g"`
        if [ -x "$CMD" -a ! -d "$CMD" ]
        then
            echo "$CMD" | sed -e "s@//*@/@g"; return
        fi
    done
}


#
# Function to locate Python tool
#
locate_python_tool() {
    for TOOL in $HOME/.local/bin/$2 /usr/local/bin/$2 $1/$2 $1/Tools/scripts/$2 $1/Scripts/$2.exe
    do
        if [ -f "$TOOL.py" -a `basename "$TOOL.py"` != "pip3.py" ]  # pip3.py is broken
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
    PYEXE=python3
    PYLD_FLAGS=
    PY_MAIN=`basename "$0"`
    case $PY_MAIN in
    7z|7za)
        PYLD_FLAGS="-pyldname=$PY_MAIN"
        PY_MAIN="p7zip"
        ;;
    bson|bz2|calendar|git|json|random|yaml)
        PYLD_FLAGS="-pyldname=$PY_MAIN"
        PY_MAIN="${PY_MAIN}_"
        ;;
    g++)
        PYLD_FLAGS="-pyldname=$PY_MAIN"
        PY_MAIN="gxx_"
        ;;
    git-*|systemd-analyze)
        PYLD_FLAGS="-pyldname=$PY_MAIN"
        PY_MAIN=`echo "$PY_MAIN" | sed -e "s/-/_/g"`
        ;;
    ipdb|pip|pydoc)
        PYEXE=python
        ;;
    python*)
        PYEXE="$PY_MAIN"
        ;;
    vi|vim)
        PYLD_FLAGS="-pyldname=$PY_MAIN"
        PY_MAIN="vi"
        ;;
    esac

    if [ "$OSTYPE" = "cygwin" ]
    then
        ARGS=
        while [ $# -gt 0 ]
        do
            if [ -f "$1" ]
            then
                ARG=`cygpath -w "$1" 2> /dev/null | sed -e "s/%/%25/g;s/ /%20/g"`
            else
                ARG=`echo "$1" | sed -e "s/%/%25/g;s/ /%20/g"`
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
            set -- "$@" "`echo \"$ARG\" | sed -e 's/%20/ /g;s/%25/%/g'`"
        done
    fi

    PYTHON=`locate_python "$@"`
    if [ ! "$PYTHON" ]
    then
        PYTHON=`which $PYEXE`
        if [ ! "$PYTHON" ]
        then
            echo "***ERROR*** Cannot find required \"`basename \"$0\"`\" software." 1>&2
            exit 1
        fi
    fi

    unset PYTHONSTARTUP PYTHONHOME
    BIN_DIR=`dirname "$0"`

    if [ "$PYEXE" = "$PY_MAIN" ]
    then
        exec $PYTHON "$@"
    fi

    if [ -f "$BIN_DIR/$PY_MAIN.py" ]
    then
        exec "$PYTHON" -B -E "$BIN_DIR/pyld.py" $PYLD_FLAGS $PY_MAIN "$@"
    fi

    if [ "$PYEXE" != "$PY_MAIN" ]
    then
        BIN_DIR=`dirname "$PYTHON"`
        TOOL=`locate_python_tool "$BIN_DIR" "$PY_MAIN"`
        if [ "$TOOL" ]
        then
            case "$TOOL" in
            *.exe)
                exec $PYTHON $TOOL "$@"
                ;;
            esac
            if [ "`head -1 \"$TOOL\" | grep '#!.*python'`" ]
            then
                exec $PYTHON $TOOL "$@"
            fi
            exec $TOOL "$@"
        fi
    fi
    if [ ! "`which \"$PY_MAIN\"`" ]
    then
        echo "***ERROR*** Cannot find required \"$PY_MAIN\" software." 1>&2
    fi
    exec `which "$PY_MAIN"` "$@"
}

cache_dotfiles
exec_python "$@"
