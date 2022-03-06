ARG BASE_IMAGE=centos:latest

FROM ${BASE_IMAGE}

# Install base packages

RUN sed -i "s/mirrorlist=/#mirrorlist=/g" /etc/yum.repos.d/CentOS-* && \
    sed -i "s@#baseurl=http://mirror.centos.org@baseurl=http://vault.centos.org@g" /etc/yum.repos.d/CentOS-* && \
    yum -y install epel-release && \
    yum -y update && \
    yum -y install \
        bind-utils \
        net-tools \
        netcat \
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
