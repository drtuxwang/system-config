FROM drtuxwang/debian

# Install sandbox environment packages
RUN apt-get install --no-install-recommends -y \
		file \
		fonts-noto-cjk \
		fonts-noto-hinted \
		libgl1-mesa-glx \
		libsdl1.2debian \
		procps \
		tmux \
		wget \
		x11-xserver-utils \
		xauth && \
	apt-get clean && \
	rm -rf /root/.??* && \
	echo "sandbox:x:99999:99999::/home/sandbox:/bin/bash" >> /etc/passwd && \
	echo "sandbox:x:99999" >> /etc/group && \
	chmod -R 777 /home && \
	wget https://github.com/krallin/tini/releases/download/v0.18.0/tini-amd64 -O /tini && \
	chmod 755 /tini

# Install compiler & dev packages
RUN apt-get install --no-install-recommends -y \
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
		uuid-dev && \
	apt-get clean

# Install WINE packages
RUN dpkg --add-architecture i386 && \
	sed -i "s/^deb http/deb [arch=amd64,i386] http/" /etc/apt/sources.list && \
	apt-get update && \
	apt-get install --no-install-recommends -y wine wine64 wine32:i386 libc6-dev:i386 && \
	apt-get clean && \
	winecfg && \
	tar cf /home/home-wine.tar -C /root .wine && \
	rm -rf /root/.??*

# Install Python packages
COPY tmpdir/etc/install-python-requirements.sh tmpdir/etc/python-requirements.txt /etc/
RUN /etc/install-python-requirements.sh /usr/bin/python3 && \
	rm -f /etc/install-python-requirements.sh /etc/python-requirements.txt

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Add home directory archive
COPY tmpdir/home.tar /home/

# Configure start
COPY tmpdir/etc/docker-init /etc/
ENTRYPOINT ["/tini", "/etc/docker-init"]
