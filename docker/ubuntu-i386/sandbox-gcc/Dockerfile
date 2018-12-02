FROM drtuxwang/ubuntu-sandbox:18.04-i386

# Install compiler & dev packages
RUN DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
		g++ \
		gfortran \
		libbz2-dev \
		libdb5.3-dev \
		libevent-dev \
		libgdbm-dev \
		liblzma-dev \
		libncurses5-dev \
		libreadline6-dev \
		libsqlite3-dev \
		libssl-dev \
		python3-dev \
		python3-setuptools \
		tk8.6-dev && \
	apt-get clean

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Add home directory archive
COPY tmpdir/home.tar /home/

# Configure start
COPY tmpdir/etc/docker-init /etc/
ENTRYPOINT ["/tini", "/etc/docker-init"]
