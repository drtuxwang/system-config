FROM clearlinux:latest

# Install base packages
RUN swupd bundle-add network-basic editors && \
	python3 -m pip install --upgrade pip

# Root account
COPY tmpdir/config/.bashrc tmpdir/config/.vimrc /root/

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
