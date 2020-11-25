#!/bin/bash -eu

KUBE_VERSION=$(docker images | grep "^k8s.gcr.io/kube-scheduler " | awk 'NR==1 {print $2}')
COREDNS_VERSION=$(docker images | grep "^k8s.gcr.io/coredns " | awk 'NR==1 {print $2}')
ETCD_VERSION=$(docker images | grep "^k8s.gcr.io/etcd " | awk 'NR==1 {print $2}')
PAUSE_VERSION=$(docker images | grep "^k8s.gcr.io/pause " | awk 'NR==1 {print $2}')
CALICO_VERSION=$(docker images | grep "^calico/cni " | awk 'NR==1 {print $2}')

FILES="
k8s.gcr.io/kube-apiserver:$KUBE_VERSION
k8s.gcr.io/kube-controller-manager:$KUBE_VERSION
k8s.gcr.io/kube-scheduler:$KUBE_VERSION
k8s.gcr.io/kube-proxy:$KUBE_VERSION
k8s.gcr.io/coredns:$COREDNS_VERSION
k8s.gcr.io/etcd:$ETCD_VERSION
k8s.gcr.io/pause:$PAUSE_VERSION
"
CREATED=$(docker inspect $FILES | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')
IMAGES_FILE="kubernetes-control-plane-${KUBE_VERSION}_images.tar"
echo "docker save $FILES -o $IMAGES_FILE"
docker save $FILES -o $IMAGES_FILE
touch -d "$CREATED" $IMAGES_FILE

FILES="
calico/cni:$CALICO_VERSION
calico/kube-controllers:$CALICO_VERSION
calico/node:$CALICO_VERSION
calico/pod2daemon-flexvol:$CALICO_VERSION
"
CREATED=$(docker inspect $FILES | sed -e 's/"/ /g' | sort -r | awk '/Created/ {print $3; exit}')
IMAGES_FILE="kubernetes-calico-cni-${CALICO_VERSION}_images.tar"
echo "docker save $FILES -o $IMAGES_FILE"
docker save $FILES -o $IMAGES_FILE
touch -d "$CREATED" $IMAGES_FILE
