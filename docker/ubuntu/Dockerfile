FROM ubuntu:18.04

# Install base packages
RUN apt-get update --fix-missing && \
	apt-get install --no-install-recommends -y \
		curl \
		dh-python \
		dnsutils \
		iproute2 \
		iputils-ping \
		net-tools \
		openssh-client \
		pciutils \
		python3 \
		python3-pip \
		vim \
		wget && \
	apt-get clean && \
	rm -rf /root/.cache
