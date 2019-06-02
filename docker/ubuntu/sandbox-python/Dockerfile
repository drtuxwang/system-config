FROM drtuxwang/ubuntu-sandbox

COPY tmpdir/etc/install-python-requirements.sh tmpdir/etc/python-requirements.txt /etc/

# Install compiler & dev packages
RUN DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
		gcc \
		make \
		python3-dev \
		python3-setuptools && \
	apt-get clean

# Install Python packages
RUN /etc/install-python-requirements.sh /usr/bin/python3 && \
	rm -f /etc/install-python-requirements.sh /etc/python-requirements.txt

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Add home directory archive
COPY tmpdir/home.tar /home/

# Configure start
COPY tmpdir/etc/docker-init /etc/
ENTRYPOINT ["/tini", "/etc/docker-init"]
