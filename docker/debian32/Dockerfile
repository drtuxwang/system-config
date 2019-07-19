FROM i386/debian:10-slim

# Install base packages
RUN apt-get update --fix-missing && \
	apt-get install --no-install-recommends -y \
		dnsutils \
		iputils-ping \
		net-tools \
		openssh-client \
		pciutils \
		python3 \
		python3-pip \
		vim && \
	apt-get clean && \
	rm -rf /root/.cache
