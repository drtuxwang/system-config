FROM drtuxwang/ubuntu-base:14.04

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
RUN apt-get install --no-install-recommends -y \
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

# Root account
COPY tmpdir/config/.??* /root/

# Configure start
COPY tmpdir/etc/docker-xinit /etc/
ENTRYPOINT ["/etc/docker-xinit"]
