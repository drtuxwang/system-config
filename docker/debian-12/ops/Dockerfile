ARG BASE_IMAGE=debian:latest
ARG DOCKER_REPO=None
ARG DOCKER_DEB=None

FROM ${BASE_IMAGE}
ARG DOCKER_REPO
ARG DOCKER_DEB

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
        procps \
        socat \
        tcptraceroute \
        vim \
        wget && \
    apt-get clean

RUN wget --progress=bar:force $DOCKER_REPO/$DOCKER_DEB && \
    dpkg -i $DOCKER_DEB && \
    rm $DOCKER_DEB

COPY rootfs/ /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
