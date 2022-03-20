ARG BASE_IMAGE=drtuxwang/alpine:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
RUN \
    # For Python build
    apk add \
        automake \
        bison \
        gcc \
        g++ \
        gfortran \
        make \
        bzip2-dev \
        db-dev \
        gdbm-dev \
        libevent-dev \
        libffi-dev \
        ncurses-dev \
        openssl-dev \
        python3-dev \
        readline-dev \
        sqlite-dev \
        xz-dev && \
    # For Python packages
    apk add blas-dev curl-dev jpeg-dev lapack-dev

COPY rootfs/ /
RUN /etc/python-packages.sh -pip /usr/bin/python3

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
