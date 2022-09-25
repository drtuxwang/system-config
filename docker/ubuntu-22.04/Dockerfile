ARG BASE_IMAGE=ubuntu:latest

FROM ${BASE_IMAGE}


# Install base packages
RUN apt-get update --fix-missing && \
    apt-get install --no-install-recommends -y \
        ca-certificates \
        curl \
        dh-python \
        dnsutils \
        iproute2 \
        iputils-ping \
        net-tools \
        netcat-openbsd \
        openssh-client \
        pciutils \
        python3 \
        socat \
        tcptraceroute \
        vim \
        wget && \
    apt-get clean
