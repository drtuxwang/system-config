#!/usr/bin/env bash
#
# K3S 1.34.7-1 (Official) portable app
#

set -e


app_settings() {
    NAME="k3s"
    VERSION="1.34.7+k3s1"
    PORT="linux64-x86"

    APP_DIRECTORY="${NAME}_${VERSION//+k3s/-}-$PORT"
    APP_FILES="
        https://github.com/k3s-io/k3s/releases/download/v$VERSION/k3s
        https://github.com/k3s-io/k3s/releases/download/v$VERSION/k3s-airgap-images-amd64.tar.zst
        ${0%.*}/k3s-server
        ${0%.*}/kubectl
    "
    APP_SHELL="
        ln -s kubectl crictl
        mv k3s k3s-${VERSION//+k3s/-}
        ln -sf k3s-${VERSION//+k3s/-} k3s
        touch -r k3s-${VERSION//+k3s/-} k3s k3s-server kubectl

        sed -e 's@image.name@\nimage.name@g;s@docker.io/@@g' index.json | \
            grep image.name | cut -f3 -d'\"' | sort > ../k3s-rancher_${VERSION//+k3s/-}.tar.list
        tar ../k3s-rancher_${VERSION//+k3s/-}.tar.7z blobs index.json manifest.json oci-layout
        touch -r ../Downloads/k3s-airgap-images-amd64.tar.zst \
            ../k3s-rancher_${VERSION//+k3s/-}.tar.*
        rm -rf blobs index.json manifest.json oci-layout
    "
    APP_START="k3s"
}

app_start() {
    MYDIR=$(realpath "${0%/*}")
    exec "$MYDIR/$APP_START" "$@"
}


source "${0%/*}/setup-software.bash" "$@" app_settings
