ARG BASE_IMAGE=drtuxwang/centos:latest

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
    # For Python packages
    yum install -y python36-devel && \
    rpm -e --nodeps python3-rpm-generators python3-rpm-macros python3-setuptools && \
    yum clean all && \
    rm -rf /var/cache/yum

COPY rootfs/ /
RUN /etc/python-packages.bash -pip /usr/bin/python3

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
