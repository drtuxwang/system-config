ARG BASE_IMAGE=clearlinux:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN swupd bundle-add network-basic socat editors && \
	swupd clean
