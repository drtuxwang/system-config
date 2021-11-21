ARG BASE_IMAGE=rockylinux/rockylinux:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN yum -y install epel-release && \
    yum -y update && \
    yum -y install \
        bind-utils \
        net-tools \
        openssh-clients \
        pciutils \
        python38 \
        socat \
        vim \
        wget && \
    rpm -e --nodeps \
        platform-python-setuptools \
        python3-pip-wheel \
        python3-setuptools-wheel \
        python38-pip \
        python38-pip-wheel \
        python38-setuptools \
        python38-setuptools-wheel && \
    yum clean all && \
    rm -rf \
        /root/.bash_logout \
        /root/.bash_profile \
        /root/.cache \
        /root/.cshrc \
        /root/.pki \
        /root/.tcshrc \
        /root/anaconda-ks.cfg
