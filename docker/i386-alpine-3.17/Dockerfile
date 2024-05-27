ARG BASE_IMAGE=i386/alpine:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN apk update && \
    apk add \
        bash \
        bind-tools \
        curl \
        iproute2 \
        openssh-client \
        socat \
        tcptraceroute \
        vim && \
    echo -e '#!/bin/bash\n/bin/uname "$@" | sed -e "s/x86_64/i386/g"' > /usr/local/bin/uname && \
    chmod ugo+rx /usr/local/bin/uname

# Install compiler & dev packages
RUN apk add \
        automake \
        bison \
        gcc \
        g++ \
        gfortran \
        make \
        bzip2-dev \
        curl-dev \
        db-dev \
        gdbm-dev \
        libevent-dev \
        libffi-dev \
        ncurses-dev \
        openssl-dev \
        readline-dev \
        sqlite-dev \
        xz-dev && \
    apk add blas-dev curl-dev jpeg-dev lapack-dev

COPY rootfs/ /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
