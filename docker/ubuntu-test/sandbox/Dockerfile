FROM drtuxwang/ubuntu-base:18.10

# Install sandbox environment packages
RUN apt-get install --no-install-recommends -y \
		file \
		libgl1-mesa-glx \
		libsdl1.2debian \
		tmux \
		wget \
		x11-xserver-utils \
		xauth && \
	apt-get clean

# Install compiler & dev packages
RUN DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
		g++ \
		gfortran \
		libbz2-dev \
		libdb5.3-dev \
		libevent-dev \
		libffi-dev \
		libgdbm-dev \
		liblzma-dev \
		libncurses5-dev \
		libreadline6-dev \
		libsqlite3-dev \
		libssl-dev \
		python3-dev \
		python3-setuptools \
		tk8.6-dev \
		uuid-dev && \
	apt-get clean

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
RUN wget https://github.com/krallin/tini/releases/download/v0.18.0/tini-amd64 -O /tini && \
		chmod 755 /tini
COPY tmpdir/etc/docker-xinit /etc/
ENTRYPOINT ["/tini", "/etc/docker-xinit"]
