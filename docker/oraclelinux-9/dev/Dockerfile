ARG BASE_IMAGE=drtuxwang/oraclelinux:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
RUN \
    # For Python build
    dnf config-manager --add-repo http://yum.oracle.com/repo/OracleLinux/OL9/codeready/builder/x86_64 && \
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
    # For Python packages
    yum install -y python3-devel && \
    yum clean all && \
    rm -rf /var/cache/yum

COPY rootfs/ /
RUN /etc/python-packages.bash -pip /usr/bin/python3

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
