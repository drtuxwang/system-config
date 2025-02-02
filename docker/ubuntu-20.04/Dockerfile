ARG BASE_IMAGE=ubuntu:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN apt-get update && \
    apt-get install --no-install-recommends --fix-missing -y \
        ca-certificates \
        curl \
        dnsutils \
        iproute2 \
        iputils-ping \
        net-tools \
        netcat-openbsd \
        openssh-client \
        pciutils \
        socat \
        tcptraceroute \
        vim \
        wget && \
    apt-get clean

# Install compiler & dev packages
RUN apt-get install --no-install-recommends --fix-missing -y \
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
        uuid-dev && \
    apt-get install --no-install-recommends --fix-missing -y \
        libcurl4-openssl-dev && \
    apt-get clean

COPY rootfs/ /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD ["bash", "-l"]
