ARG BASE_IMAGE=debian:latest

FROM ${BASE_IMAGE}


# Install base packages
RUN apt-get update --fix-missing && \
    apt-get install --no-install-recommends -y \
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
        python3 \
        socat \
        tcptraceroute \
        vim \
        wget && \
    apt-get clean && \
    rm /usr/lib/python*/EXTERNALLY-MANAGED
