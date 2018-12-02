FROM drtuxwang/ubuntu-sandbox:18.04

# Install WINE packages
RUN apt-get install --no-install-recommends -y firefox fonts-noto-cjk fonts-noto-hinted && \
	apt-get clean

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Add home directory archive
COPY tmpdir/home.tar /home/

# Configure start
COPY tmpdir/etc/docker-init /etc/
ENTRYPOINT ["/tini", "/etc/docker-init"]
