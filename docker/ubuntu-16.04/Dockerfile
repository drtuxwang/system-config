ARG BASE_IMAGE=ubuntu:latest

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
		vim \
		wget && \
	apt-get clean && \
	rm -rf /root/.cache
