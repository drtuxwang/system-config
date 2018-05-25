FROM debian:8

# Install base packages
RUN apt-get update && \
	apt-get install --no-install-recommends -y \
		net-tools \
		openssh-client \
		pciutils \
		python3 \
		python3-pip \
		vim && \
	apt-get clean && \
	python3 -m pip install --upgrade pip

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
