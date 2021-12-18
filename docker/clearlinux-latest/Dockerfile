ARG BASE_IMAGE=clearlinux:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN swupd bundle-add diffutils network-basic socat editors which && \
    swupd clean
