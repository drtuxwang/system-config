#!/usr/bin/env bash
#
# Bash portable app module
# - Build and run Linux portable apps
#
# Copyright GPL v2: 2025 By Dr Colin Kong
#

set -u


defaults_settings() {
    APP_DIRECTORY=/unknown
    APP_FILES=
    APP_UNPACK=
    APP_REMOVE=
    APP_SHELL=
    APP_START=
    APP_LINK=
}

get_files() {
    for FILE in $APP_FILES
    do
        echo -e "\033[33m=> $FILE\033[0m"
        [ -f "${FILE##*/}" ] && continue
        case $FILE in
        *://*)
            wget --timestamping "$FILE" || exit 1
            ;;
        */*)
            cp -p $FILE .
            ;;
        *)
            echo "Missing: Downloads/$FILE"
            exit 1
            ;;
        esac
    done
}

unpack_file() {
    echo -e "\033[33m=> $1\033[0m"
    case $1 in
    *.deb)
        rm -f control.tar.* data.tar.* debian-binary
        ar x $1 || exit 1
        tar xf data.tar.* || exit 1
        rm -f control.tar.* data.tar.* debian-binary
        ;;
    *.tar*)
        tar xf $1 || exit 1
        ;;
    *)
        7z x -y -snld $1 || exit 1
        ;;
    esac
}

remove_file() {
    if [ -d "$1" ]
    then
        echo -e "\033[33m=> rm -r $1/\033[0m"
        rm -r $1 || exit 1
    elif [ -f "$1" ]
    then
        echo -e "\033[33m=> rm -r $1\033[0m"
        rm -r $1 || exit 1
    fi
}

prepare_files() {
    for FILE in $APP_FILES
    do
        unpack_file "../Downloads/${FILE##*/}"
    done
    for FILE in $APP_UNPACK
    do
        unpack_file $FILE
    done
    for FILE in $APP_REMOVE
    do
        remove_file "${FILE%/}"
    done
    if [ "$APP_SHELL" ]
    then
        echo -e "\033[33m=> #!/usr/bin/env bash\033[0m"
        echo "$APP_SHELL" | bash -ex || exit 1
    fi
}

prepare_start() {
    echo -e "\033[33m=> du -k $APP_DIRECTORY\033[0m"
    du -k $APP_DIRECTORY | sort -k 2

    if [ "$APP_START" ]
    then
        echo -e "\033[33m=> $APP_DIRECTORY/$APP_START\033[0m"
        if [ "$APP_LINK" ]
        then
            if [ "${APP_START##*/}" != "$APP_START" ]
            then
                echo -e "\033[33m=> $APP_DIRECTORY/${APP_START##*/}\033[0m"
                sed -e "s/^source.*/app_settings\napp_start/" "$0" > \
                    "$APP_DIRECTORY/${APP_START##*/}"
                chmod ugo+x "$APP_DIRECTORY/${APP_START##*/}"
                touch -r "$APP_DIRECTORY/$APP_START" "$APP_DIRECTORY/${APP_START##*/}"
            fi
            if [ "$APP_LINK" != "${APP_START##*/}" ]
            then
                echo -e "\033[33m=> $APP_DIRECTORY/$APP_LINK\033[0m"
                ln -sf "${APP_START##*/}" "$APP_DIRECTORY/$APP_LINK"
                touch -h -r "$APP_DIRECTORY/$APP_START" "$APP_DIRECTORY/$APP_LINK"
            fi
        fi
    fi

    PATH=../bin:$PATH fmod -R "$APP_DIRECTORY" > /dev/null 2>&1
    EMPTY=$(find "$APP_DIRECTORY" -type d -empty)
    [ "$EMPTY" ] && echo "$EMPTY" && exit 1
    echo -e "\033[33m=> DONE!\033[0m"
}

create_app() {
    umask 022

    mkdir -p Downloads
    cd Downloads
    get_files

    rm -rf "../$APP_DIRECTORY.part"
    mkdir "../$APP_DIRECTORY.part" || exit 1
    cd "../$APP_DIRECTORY.part"
    prepare_files

    cd ..
    rm -rf "$APP_DIRECTORY"
    mv "$APP_DIRECTORY.part" "$APP_DIRECTORY"
    prepare_start
}


cd "${0%/*}"
defaults_settings
app_settings
create_app
