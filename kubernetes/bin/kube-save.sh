#!/usr/bin/env bash
#
# Save images used by Kubernetes as tar archives
#

set -eu

create_backup() {
    FILE=$1
    shift

    LIST="${FILE%.tar}.list"
    CREATED=$(docker inspect $* | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')
    if [ -f "$FILE.7z" ]
    then
        echo "Skipping existing file: $(realpath $FILE.7z)"
    else
        echo "docker save $* -o $FILE"
        docker save $* -o "$FILE.part"
        tar xf "$FILE.part" repositories -O | sed -e "s/,/\\n/g;s/\"/:/g" | cut -f2,5 -d: > "$LIST.part"
        touch -d $CREATED "$FILE.part" "$LIST.part"
        mv "$FILE.part" "$FILE"
        mv "$LIST.part" "$LIST"
        7z a -m0=lzma2 -mmt=2 -mx=9 -myx=9 -md=128m -mfb=256 -ms=on -snh -snl -stl -y "$FILE.7z.part" "$FILE"
        mv "$FILE.7z.part" "$FILE.7z"
        rm "$FILE"
        echo "Created archive file: $(realpath $FILE.7z)"
    fi
}


save_calico() {
   IMAGES=$(kubectl -n kube-system get pod -o yaml | awk '/image: calico\// {print $NF}' | sort | uniq)
   [ ! "$IMAGES" ] && return

   VERSION=$(echo "$IMAGES" | awk '/calico\/cni/ {print $NF; exit}' | sed -e "s/.*://")
   create_backup calico-cni_$VERSION.tar $IMAGES
}


save_k8s() {
   IMAGES=$(kubectl -n kube-system get pod -o yaml | awk '/image: k8s.gcr.io\// {print $NF}' | sort | uniq)
   [ ! "$IMAGES" ] && return

   VERSION=$(kubectl get nodes 2> /dev/null | awk '/Ready / {print $NF; exit}')
   create_backup k8s-gcr-io_$VERSION.tar $IMAGES \
       $(docker images | awk '/k8s.gcr.io\/pause/ {printf("%s:%s\n", $1, $2); exit}')
}


save_k3s() {
   IMAGES=$(kubectl -n kube-system get pod -o yaml | awk '/image: rancher\// {print $NF}' | sort | uniq)
   [ ! "$IMAGES" ] && return

   VERSION=$(kubectl get nodes 2> /dev/null | awk '/Ready / {print $NF; exit}')
   create_backup k3s-rancher_$VERSION.tar $IMAGES \
       $(docker images | awk '/rancher\/mirrored-pause/ {printf("%s:%s\n", $1, $2); exit}')
}


umask 022
save_calico
save_k8s
save_k3s
