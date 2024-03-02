#!/usr/bin/env bash
#
# Bash Docker utilities module
#
# Copyright GPL v2: 2018-2024 By Dr Colin Kong
#


set -u


#
# Function to parse options
#
options() {
    help() {
        echo "Usage: $0 <options>"
        echo
        echo "docker-list     - List Docker images/volumes/containers/networks"
        echo "docker-images   - Show Docker images with optional filter"
        echo "docker-load     - Load Docker image archives \"tar|tar.gz|tar.bz2|tar.xz|t[bgx]z\""
        echo "docker-save     - Save images as \"tar.7z\" archives"
        echo "docker-prune    - Run prune to remove unused Docker data"
        echo
        echo "Options:"
        echo "  -h, --help  Show this help message and exit"
        echo "  <pattern>   Regular expression pattern for docker-images."
        echo "  <tar-file>  Image tar file for docker-load."
        echo "  <image>     Image name for docker-save and docker-save-new."
        exit $1
    }

    case "${0##*/}" in
    *list*)
        mode=list
        ;;
    *images*)
        mode=images
        ;;
    *load*)
        mode=load
        ;;
    *save*)
        mode=save
        ;;
    *prune*)
        mode=prune
        ;;
    *)
        help 0
        ;;
    esac
    while getopts "h" option
    do
        case $option in
        h)
            help 0
            ;;
        *)
            help 1
            ;;
        esac
    done
    shift $((OPTIND - 1))
    case ${1:-} in
    --help)
      help 0
      ;;
    --*)
      help 1
      ;;
    esac
}


#
# Function to list Docker images/volumes/containers/networks
#
docker_list() {
    PATTERN="$(echo "$@" | sed -e "s/ /|/g")"

    docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}"
    echo
    docker volume ls
    echo
    docker ps
    echo
    docker system df
    echo
    df /var/lib/docker
    echo
    docker network ls
}


#
# Function to show Docker images with optional filter
#
docker_images() {
    if [ $# = 0 ]
    then
        docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}"
    else
        docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}" | grep -E "^REPOSITORY:TAG|$(echo "$@" | sed -e "s/ /|/g")" | sort
    fi
}



#
# Load Docker image archives "tar|tar.gz|tar.bz2|tar.xz|t[bgx]z"
#
docker_load() {
    while [ $# != 0 ]
    do
        FILE="$1"
        case "$FILE" in
        *.tar.7z|*.t7z)
            echo "7z x -so \"$FILE\" | docker load"
            7z x -so "$FILE" | docker load
            ;;
        *.tar|*.tar.gz|*.tar.bz2|*.tar.xz|*.t[bgx]z)
            echo "docker load -i \"$FILE\""
            docker load -i "$FILE"
            ;;
        esac
        shift
    done
}


#
# Save images as "tar.7z" archives
#
docker_save() {
    umask 022
    for IMAGE in $*;
    do
        CREATED=$(docker inspect "$IMAGE" | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')
        FILE=$(echo $IMAGE | sed -e "s/\//-/g;s/:/_/")_$(echo $CREATED | sed -e "s/-//g;s/T.*//").tar
        if [ -f "$FILE.7z" ]
        then
            echo "Skipping existing file: $(realpath $FILE.7z)"
        else
            [ ! "$CREATED" ] && continue
            echo "docker save $IMAGE -o $FILE.7z"
            docker save "$IMAGE" | 7z a -m0=lzma2 -mmt=2 -mx=9 -myx=9 -md=128m -mfb=256 -ms=on -snh -snl -stl -y "$FILE.7z.part" || exit 1
            [ ${PIPESTATUS[0]} != 141 ] && exit 1
            echo "$IMAGE" > "$FILE.list"
            touch -d $CREATED "$FILE.part" "$FILE.list.part"
            mv "$FILE.7z.part" "$FILE.7z"
        fi
        shift
    done
}


#
# Function to run prune to remove unused Docker data
#
docker_prune() {
    docker system df
    echo
    df /var/lib/docker
    echo
    docker system prune
    echo
    docker system df
    echo
    df /var/lib/docker
}


options "$@"

docker_$mode "$@"
