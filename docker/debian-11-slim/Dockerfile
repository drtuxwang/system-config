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
        openssh-client \
        pciutils \
        python3 \
        socat \
        vim \
        wget && \
    apt-get clean
