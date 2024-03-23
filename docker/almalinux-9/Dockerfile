ARG BASE_IMAGE=almalinux:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN yum install -y epel-release && \
    yum update -y && \
    yum install -y \
        bind-utils \
        diffutils \
        net-tools \
        netcat \
        openssh-clients \
        pciutils \
        procps \
        python3 \
        socat \
        traceroute \
        vim \
        wget && \
    rpm -e --nodeps \
        python3-pip-wheel \
        python3-setuptools-wheel && \
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
