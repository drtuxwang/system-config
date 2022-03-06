ARG BASE_IMAGE=drtuxwang/amazonlinux:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
RUN \
    # For Python build
    yum -y install \
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
        ncurses-devel \
        openssl-devel \
        readline-devel \
        uuid-devel \
        xz-devel && \
    # For Python packages
    yum -y install python3-devel && \
    rpm -e --nodeps python3-rpm-macros python3-setuptools && \
    yum clean all

COPY root-disk/ /
RUN /etc/python-packages.sh -pip /usr/bin/python3

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
