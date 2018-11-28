FROM drtuxwang/ubuntu-base:18.04-i386

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

# Configure start
RUN wget https://github.com/krallin/tini/releases/download/v0.18.0/tini-i386 -O /tini && \
	chmod 755 /tini && \
	rm -f /root/.wget-hsts
COPY tmpdir/etc/docker-init /etc/
ENTRYPOINT ["/tini", "/etc/docker-init"]

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Add home directory archive
COPY tmpdir/home.tar /home/

# Sandbox account
RUN echo "sandbox:x:99999:99999::/home/sandbox:/bin/bash" >> /etc/passwd && \
	echo "sandbox:x:99999" >> /etc/group && \
	chmod -R 777 /home && \
	rm -rf /root
