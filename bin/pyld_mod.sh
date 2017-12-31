#!/bin/sh
#
# Python loader module
#
VERSION=20171231


#
# Function to locate Python command
#
locate_python() {
    case $1 in
    */ibus/*|*/meld)  # Must use system Python
        return
    esac

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
# Function to locate Python tool
#
locate_python_tool() {
    for TOOL in $1/$2.py $1/$2 $1/Tools/scripts/$2.py $1/Scripts/$2.exe
    do
        if [ -f "$TOOL" ]
        then
            echo "$TOOL"
            return
        fi
    done
}


#
# Function to return location of program
#
which() {
    if [ "$1" = "`basename $0`" ]
    then
        PATH=`echo ":$PATH:" | sed -e "s@:\`dirname \"$0\"\`:@@"`
    fi

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
# Execute Python or Python tool
#
exec_python() {
    PY_MAIN=`basename "$0"`
    case $PY_MAIN in
    python*)
        PYEXE="$PY_MAIN"
        ;;
    ipdb|pip|pydoc)
        PYEXE=python
        ;;
    *)
        PYEXE=python3
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
    if [ "$PYTHON" ]
    then
        if [ "$PYEXE" != "$PY_MAIN" ]
        then
            BIN_DIR=`dirname "$PYTHON"`
            TOOL=`locate_python_tool "$BIN_DIR" "$PY_MAIN"`
            if [ "$TOOL" ]
            then
                exec $PYTHON $TOOL "$@"
            fi
        fi
    else
        PYTHON=`which \`basename "$0"\``
        if [ ! "$PYTHON" ]
        then
            echo "***ERROR*** Cannot find required \"`basename \"$0\"`\" software." 1>&2
            exit 1
        fi
    fi

    unset PYTHONSTARTUP PYTHONHOME
    if [ ! "`echo \":$PATH:\" | grep \":\`dirname $0\`:\"`" ]
    then
        PATH=`dirname $0`:$PATH; export PATH
    fi

    if [ "$PYEXE" = "$PY_MAIN" ]
    then
        exec $PYTHON "$@"
    else
        if [ ! "`which \"$PY_MAIN\"`" ]
        then
            echo "***ERROR*** Cannot find required \"$PY_NAME\" software." 1>&2
        fi
        exec `which "$PY_MAIN"` "$@"
    fi
}
