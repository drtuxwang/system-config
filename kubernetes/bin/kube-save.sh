#!/usr/bin/env bash

set -eu

KUBE_VERSION=$(docker images | grep "^k8s.gcr.io/kube-scheduler " | awk 'NR==1 {print $2}')
COREDNS_VERSION=$(docker images | grep "^k8s.gcr.io/coredns " | awk 'NR==1 {print $2}')
ETCD_VERSION=$(docker images | grep "^k8s.gcr.io/etcd " | awk 'NR==1 {print $2}')
PAUSE_VERSION=$(docker images | grep "^k8s.gcr.io/pause " | awk 'NR==1 {print $2}')
CALICO_VERSION=$(docker images | grep "^calico/cni " | awk 'NR==1 {print $2}')

IMAGES="
k8s.gcr.io/kube-apiserver:$KUBE_VERSION
k8s.gcr.io/kube-controller-manager:$KUBE_VERSION
k8s.gcr.io/kube-scheduler:$KUBE_VERSION
k8s.gcr.io/kube-proxy:$KUBE_VERSION
k8s.gcr.io/coredns:$COREDNS_VERSION
k8s.gcr.io/etcd:$ETCD_VERSION
k8s.gcr.io/pause:$PAUSE_VERSION
"
FILE="kubernetes-images_control-plane_${KUBE_VERSION}.tar"
LIST="${FILE%.tar}.list"
CREATED=$(docker inspect $IMAGES | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')

echo "docker save $IMAGES -o $FILE"
docker save $IMAGES -o "$FILE.part"
tar xf "$FILE.part" repositories -O | sed -e "s/,/\\n/g;s/\"/:/g" | cut -f2,5 -d: > "$LIST.part"
touch -d $CREATED "$FILE.part" "$LIST.part"
chmod 644 "$FILE.part"
mv "$FILE.part" "$FILE"
mv "$LIST.part" "$LIST"

IMAGES="
calico/cni:$CALICO_VERSION
calico/kube-controllers:$CALICO_VERSION
calico/node:$CALICO_VERSION
calico/pod2daemon-flexvol:$CALICO_VERSION
"
FILE="kubernetes-images_calico-cni_${CALICO_VERSION}.tar"
LIST="${FILE%.tar}.list"
CREATED=$(docker inspect $IMAGES | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')

echo "docker save $IMAGES -o $FILE"
docker save $IMAGES -o "$FILE.part"
tar xf "$FILE.part" repositories -O | sed -e "s/,/\\n/g;s/\"/:/g" | cut -f2,5 -d: > "$LIST.part"
touch -d $CREATED "$FILE.part" "$LIST.part"
chmod 644 "$FILE.part"
mv "$FILE.part" "$FILE"
mv "$LIST.part" "$LIST"
