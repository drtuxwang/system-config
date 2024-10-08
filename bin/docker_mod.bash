#!/usr/bin/env bash
#
# Bash Docker utilities module
#
# Copyright GPL v2: 2018-2024 By Dr Colin Kong
#

set -u

IMAGE_SED="s/^REPOSITORY:TAG .*/REPOSITORY:TAG IMAGE ID CREATED AT       SIZE/"


#
# Function to parse options
#
options() {
    help() {
        echo "Usage: $0 <options>"
        echo
        echo "docker-list     - List Docker images/volumes/containers/networks"
        echo "docker-images   - Show Docker images with optional filter"
        echo "docker-pull     - Pull Docker images"
        echo "docker-tag      - Tag Docker image with name and add promoted label"
        echo "docker-push     - Push Docker images"
        echo "docker-load     - Load Docker image archives \"tar|tar.gz|tar.bz2|tar.xz|tar.7z|t[bgx7]z\""
        echo "docker-save     - Save images as \"tar.7z\" archives"
        echo "docker-prune    - Run prune to remove unused Docker data"
        echo
        echo "Options:"
        echo "  -h, --help  Show this help message and exit."
        echo "  <pattern>   Regular expression pattern for docker-images."
        echo "  <tar-file>  Image tar file for docker-load."
        echo "  <image>     Image name for docker-save and docker-save-new."
        exit $1
    }

    case "${0##*/}" in
    *-list|*-images|*-pull|*-push|*-load|*-save|*-prune)
        mode=${0##*-}
        ;;
    *-tag)
        [ $# = 0 ] && help 1
        mode=${0##*-}
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
    PATTERN="$(echo "$@" | tr " " "|")"

    docker_images
    echo
    docker volume ls | sed -e "s/^DRIVER .*/DRIVER VOLUME_NAME/" | column -t
    echo
    docker ps | sed -e "s/^CONTAINER ID /CONTAINER_ID/" | column -t
    echo
    docker system df
    echo
    df /var/lib/docker | sed -e "s/Mounted *on$/Mounted_on/" | column -t
    echo
    docker network ls | sed -e "s/^NETWORK ID/NETWORK_ID/" | column -t
}

#
# Function to show Docker images with optional filter
#
docker_images() {
    IMAGES=$(docker images --format "table {{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}" | tail -n +2 | sed -e "s/ \([0-9][0-9]:[0-9][0-9]:[0-9][0-9]\)/T\1 /" | awk '{printf("%s %s %s%s %s\n", $1, $2, $3, $4, $6)}')
    [ $# != 0 ] && IMAGES=$(echo "$IMAGES" | grep -E "$(echo "$@" | sed -e "s/ /|/g;s/||/ |/g;s/|$/ /")")
    (echo "REPOSITORY:TAG IMAGE ID CREATED AT SIZE"; echo "$IMAGES") | sort | column -t
}

#
# Pull Docker images
#
docker_pull() {
    while [ $# != 0 ]
    do
        echo "docker pull \"$1\""
        docker pull "$1" || exit 1
        shift
    done
}

#
# Tag Docker image with name and add promoted label
#
docker_tag() {
    SOURCE=$1
    shift
    ${0%/*}/docker-images "^$SOURCE "
    docker inspect "$SOURCE" | sed -n '/"Labels": {/,/}/p'
    PROMOTED=$(docker inspect "$SOURCE" 2> /dev/null  | grep '"promoted": "' | sed -e 's/.*"promoted": "//;s/"$/, /')
    for TARGET in $*
    do
        echo "FROM $SOURCE" | docker build --label "promoted=$PROMOTED$SOURCE" -t "$TARGET" -
        ${0%/*}/docker-images "^$TARGET "
        docker inspect "$TARGET" | sed -n '/"Labels": {/,/}/p'
    done
}

#
# Push Docker images
#
docker_push() {
    while [ $# != 0 ]
    do
        echo "docker push \"$1\""
        docker push "$1" || exit 1
        shift
    done
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
        CREATED=$(docker inspect "$IMAGE" | tr '"' ' ' | sort -r | awk '/Created/ {print $3; exit}')
        FILE=$(echo $IMAGE | tr "/:" "-_")_$(echo $CREATED | sed -e "s/-//g;s/T.*//").tar
        if [ -f "$FILE.7z" ]
        then
            echo "Skipping existing file: $(realpath $FILE.7z)"
        else
            [ ! "$CREATED" ] && continue
            echo "docker save $IMAGE -o $FILE.7z"
            docker save "$IMAGE" | 7z a -m0=lzma2 -mmt=2 -mx=9 -myx=9 -md=128m -mfb=256 -ms=on -snh -snl -stl -si -y "$FILE.7z.part" || exit 1
            [ ${PIPESTATUS[0]} != 0 ] && exit 1
            echo "$IMAGE" > "$FILE.list"
            touch -d $CREATED "$FILE.7z.part" "$FILE.list"
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
