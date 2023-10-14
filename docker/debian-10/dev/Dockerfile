ARG BASE_IMAGE=drtuxwang/debian:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
RUN \
    # For Python build
    apt-get install --no-install-recommends --fix-missing -y \
        automake \
        bison \
        g++ \
        gfortran \
        libbz2-dev \
        libdb5.3-dev \
        libevent-dev \
        libffi-dev \
        libgdbm-dev \
        liblzma-dev \
        libncurses5-dev \
        libreadline6-dev \
        libsqlite3-dev \
        libssl-dev \
        make \
        pkg-config \
        python3-dev \
        uuid-dev && \
    # For Python packages
    apt-get install --no-install-recommends --fix-missing -y \
        libcurl4-openssl-dev && \
    apt-get clean

COPY rootfs/ /
RUN /etc/python-packages.bash -pip /usr/bin/python3

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
