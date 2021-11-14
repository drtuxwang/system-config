ARG BASE_IMAGE=drtuxwang/i386-debian:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
RUN \
    # For Python build
    apt-get install --no-install-recommends -y \
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
        python3-dev \
        uuid-dev && \
    # For Python packages
    apt-get install --no-install-recommends -y libcurl4-openssl-dev make && \
    apt-get clean

# Install Python packages
COPY tmpdir/python-packages.sh tmpdir/python-requirements*.txt* /etc/
RUN /etc/python-packages.sh -pip /usr/bin/python3 && \
    apt-get clean

ADD tmpdir/root.tar /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
