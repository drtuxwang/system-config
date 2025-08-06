ARG BASE_IMAGE=oraclelinux:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN ln -s microdnf /bin/yum && \
    yum install -y epel-release && \
    yum update -y && \
    yum install -y \
        bind-utils \
        diffutils \
        file \
        net-tools \
        netcat \
        openssh-clients \
        pciutils \
        procps \
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
RUN dnf config-manager --add-repo http://yum.oracle.com/repo/OracleLinux/OL9/codeready/builder/x86_64 && \
    yum install -y \
        automake \
        bison \
        gcc-c++ \
        gcc-gfortran \
        make \
        pkg-config \
        bzip2-devel \
        gdbm-devel \
        libcurl-devel \
        libdb-devel \
        libevent-devel \
        libffi-devel \
        libsqlite3x-devel \
        libuuid-devel \
        ncurses-devel \
        openssl-devel \
        readline-devel \
        xz-devel \
        zlib-devel && \
    yum clean all && \
    rm -rf /var/cache/yum

COPY rootfs/ /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD ["bash", "-l"]
