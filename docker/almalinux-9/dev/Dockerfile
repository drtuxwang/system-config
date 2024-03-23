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
    yum install --enablerepo=crb -y gdbm-devel && \
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
