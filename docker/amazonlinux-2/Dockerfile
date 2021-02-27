ARG BASE_IMAGE=amazonlinux:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN yum -y update && \
	yum -y install \
		bind-utils \
		iproute \
		net-tools \
		openssh-clients \
		pciutils \
		python3 \
		vim \
		wget && \
	yum clean all
