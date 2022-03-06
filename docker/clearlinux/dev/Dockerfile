ARG BASE_IMAGE=drtuxwang/clearlinux:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
# Python missing: _bz2 _dbm _gdbm
RUN \
    # For Python build
    swupd bundle-add \
        c-basic \
        make \
        devpkg-ncurses \
        devpkg-openssl \
        devpkg-readline \
        devpkg-sqlite-autoconf \
        devpkg-xz && \
    # For Python packages
    swupd bundle-add devpkg-curl && \
    swupd clean

COPY root-disk/ /
RUN /etc/python-packages.sh -pip /usr/bin/python3

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
