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
        echo "docker-list   - List Docker images/volumes/containers/networks"
        echo "docker-images - Show Docker images with optional filter"
        echo "docker-prune  - Run prune to remove unused Docker data"
        echo
        echo "Options:"
        echo "  -h, --help  Show this help message and exit"
        echo "  <pattern>   Regular expression pattern."
        exit $1
    }

    case "${0##*/}" in
    *list*)
        mode=list
        ;;
    *images*)
        mode=images
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
