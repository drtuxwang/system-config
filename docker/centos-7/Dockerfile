ARG BASE_IMAGE=centos:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN yum install -y epel-release && \
    yum update -y && \
    yum install -y \
        bind-utils \
        iproute \
        net-tools \
        netcat \
        openssh-clients \
        pciutils \
        python36 \
        socat \
        traceroute \
        vim \
        wget && \
    rpm -e --nodeps python3-pip python3-setuptools && \
    yum clean all && \
    rm -rf /var/cache/yum && \
    rm -rf \
        /root/.bash_logout \
        /root/.bash_profile \
        /root/.cache \
        /root/.cshrc \
        /root/.pki \
        /root/.tcshrc \
        /root/anaconda-ks.cfg
