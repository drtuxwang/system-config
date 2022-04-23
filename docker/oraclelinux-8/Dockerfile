ARG BASE_IMAGE=oraclelinux:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN ln -s microdnf /usr/bin/yum && \
    yum install -y oracle-epel-release-el8 && \
    yum update -y && \
    yum install -y \
        bind-utils \
        diffutils \
        net-tools \
        netcat \
        openssh-clients \
        pciutils \
        procps \
        socat \
        python38 \
        vim \
        wget && \
    rpm -e --nodeps \
        platform-python-setuptools \
        python3-pip-wheel \
        python3-setuptools-wheel \
        python38-pip-wheel \
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