FROM clearlinux:latest

# Install base packages
RUN swupd bundle-add network-basic editors && \
	python3 -m pip install --upgrade pip

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
