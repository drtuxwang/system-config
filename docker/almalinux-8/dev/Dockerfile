ARG BASE_IMAGE=drtuxwang/almalinux:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
RUN \
    # For Python build
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
        xz-devel && \
    # For Python packages
    yum install -y python38-devel && \
    yum clean all

COPY rootfs/ /
RUN /etc/python-packages.sh -pip /usr/bin/python3

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
