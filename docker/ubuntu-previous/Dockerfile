FROM ubuntu:14.04

# Install base packages
RUN apt-get update && \
	apt-get install --no-install-recommends -y \
		iputils-ping \
		net-tools \
		openssh-client \
		pciutils \
		python3-pip \
		vim && \
	apt-get clean && \
	python3 -m pip install --upgrade pip

# Root account
COPY tmpdir/config/.bashrc tmpdir/config/.vimrc /root/

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
