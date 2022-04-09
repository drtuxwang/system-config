ARG BASE_IMAGE=oraclelinux:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN yum install -y oracle-epel-release-el7 && \
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
        vim \
        wget && \
    rpm -e --nodeps python3-pip python3-setuptools && \
    yum clean all && \
    rm -rf \
        /root/.bash_logout \
        /root/.bash_profile \
        /root/.cache \
        /root/.cshrc \
        /root/.pki \
        /root/.tcshrc \
        /root/anaconda-ks.cfg
