ARG BASE_IMAGE=drtuxwang/centos:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
RUN \
    # For Python build
    yum -y install \
        gcc-c++ \
        gcc-gfortran \
        make \
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
    yum -y install python38-devel && \
    yum clean all

# Install Python packages
COPY tmpdir/install-python-requirements.sh tmpdir/python-requirements*.txt* /etc/
RUN /etc/install-python-requirements.sh /usr/bin/python3 piponly

ADD tmpdir/root.tar /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
