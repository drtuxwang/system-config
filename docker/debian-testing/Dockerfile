FROM debian:testing

# Install base packages
RUN apt-get update && \
	apt-get install --no-install-recommends -y \
		net-tools \
		openssh-client \
		pciutils \
		python3 \
		python3-pip \
		vim && \
	apt-get clean

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/config/bashrc /root/.bashrc
COPY tmpdir/config/vimrc /root/.vimrc

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
