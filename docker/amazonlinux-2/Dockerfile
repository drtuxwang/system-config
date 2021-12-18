ARG BASE_IMAGE=amazonlinux:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN yum -y update && \
    yum -y install \
        bind-utils \
        iproute \
        net-tools \
        netcat \
        openssh-clients \
        pciutils \
        python3 \
        socat \
        vim \
        wget && \
    rpm -e --nodeps python3-pip python3-setuptools && \
    yum clean all
