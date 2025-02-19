ARG BASE_IMAGE=centos:latest

FROM ${BASE_IMAGE}

# Switch to CentOS-7.9.2009 vault
COPY CentOS-Base.repo CentOS-CR.repo /etc/yum.repos.d/

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
        socat \
        traceroute \
        vim \
        wget && \
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

# Install compiler & dev packages
RUN yum install -y \
        automake \
        bison \
        gcc-c++ \
        gcc-gfortran \
        make \
        pkg-config \
        bzip2-devel \
        gdbm-devel \
        libdb-devel \
        libcurl-devel \
        libevent-devel \
        libffi-devel \
        libsqlite3x-devel \
        ncurses-devel \
        openssl-devel \
        readline-devel \
        uuid-devel \
        xz-devel \
        zlib-devel && \
    yum clean all && \
    rm -rf /var/cache/yum

COPY rootfs/ /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD ["bash", "-l"]
