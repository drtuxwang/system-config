ARG BASE_IMAGE=oraclelinux:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN ln -s microdnf /bin/yum && \
    yum install -y epel-release && \
    yum update -y && \
    yum install -y \
        bind-utils \
        diffutils \
        net-tools \
        netcat \
        openssh-clients \
        pciutils \
        procps \
        python38 \
        socat \
        traceroute \
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
    rm -rf /var/cache/yum && \
    rm -rf \
        /root/.bash_logout \
        /root/.bash_profile \
        /root/.cache \
        /root/.cshrc \
        /root/.pki \
        /root/.tcshrc \
        /root/anaconda-ks.cfg
