#!/bin/sh

KUBE_VERSION=$(docker images | grep "^k8s.gcr.io/kube-scheduler " | awk 'NR==1 {print $2}')
COREDNS_VERSION=$(docker images | grep "^k8s.gcr.io/coredns " | awk 'NR==1 {print $2}')
ETCD_VERSION=$(docker images | grep "^k8s.gcr.io/etcd " | awk 'NR==1 {print $2}')
PAUSE_VERSION=$(docker images | grep "^k8s.gcr.io/pause " | awk 'NR==1 {print $2}')
CALICO_VERSION=$(docker images | grep "^calico/cni " | awk 'NR==1 {print $2}')

echo "Creating kube-$KUBE_VERSION.tar..."
docker save \
    k8s.gcr.io/kube-apiserver:$KUBE_VERSION \
    k8s.gcr.io/kube-controller-manager:$KUBE_VERSION \
    k8s.gcr.io/kube-scheduler:$KUBE_VERSION \
    k8s.gcr.io/kube-proxy:$KUBE_VERSION \
    -o kube-$KUBE_VERSION.tar

echo "Creating kube-coredns-$COREDNS_VERSION.tar..."
docker save k8s.gcr.io/coredns:$COREDNS_VERSION -o kube-coredns-$COREDNS_VERSION.tar

echo "Creating kube-etcd-$ETCD_VERSION.tar..."
docker save k8s.gcr.io/etcd:$ETCD_VERSION -o kube-etcd-$ETCD_VERSION.tar

echo "Creating kube-pause-$PAUSE_VERSION.tar..."
docker save k8s.gcr.io/pause:$PAUSE_VERSION -o kube-pause-$PAUSE_VERSION.tar

echo "Creating kube-calico-$CALICO_VERSION.tar..."
docker save \
    calico/cni:$CALICO_VERSION \
    calico/kube-controllers:$CALICO_VERSION \
    calico/node:$CALICO_VERSION \
    calico/pod2daemon-flexvol:$CALICO_VERSION \
    -o kube-calico-$CALICO_VERSION.tar

ls -l kube-*.tar
