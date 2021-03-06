ARG BASE_IMAGE=drtuxwang/debian:latest

FROM ${BASE_IMAGE}

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
		uuid-dev \
		libcurl4-openssl-dev && \
	apt-get clean

# Install user environment packages
RUN apt-get install --no-install-recommends -y \
		file \
		fonts-noto-cjk \
		fonts-noto-hinted \
		libgl1-mesa-glx \
		libsdl1.2debian \
		openssh-server \
		procps \
		sudo \
		tmux \
		x11-xserver-utils \
		xauth && \
	apt-get clean && \
	mkdir -p /var/run/sshd && \
	wget https://github.com/krallin/tini/releases/download/v0.19.0/tini-amd64 -O /tini && \
	chmod 755 /tini

# Install XFCE & VNC
RUN DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
		xorg \
		dbus-x11 \
		xfce4 \
		xfce4-goodies \
		tigervnc-standalone-server \
		tigervnc-common && \
	apt-get clean

# Install WINE packages
RUN dpkg --add-architecture i386 && \
	apt-get update && \
	sed -i "s/^deb http/deb [arch=amd64,i386] http/" /etc/apt/sources.list && \
	apt-get install --no-install-recommends -y wine wine64 wine32:i386 libc6-dev:i386 && \
	apt-get clean

# Install Python packages
COPY tmpdir/etc/install-python-requirements.sh tmpdir/etc/python-requirements.txt /etc/
RUN /etc/install-python-requirements.sh /usr/bin/python3 && \
	rm -f /etc/install-python-requirements.sh /etc/python-requirements.txt

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Add home directory archive
COPY tmpdir/home.tar /home/

# Setup accounts
RUN rm -rf /root/.??* && \
	tar xf /home/home.tar -C /root && \
	useradd --shell /bin/bash --gid users owner && \
	addgroup owner sudo && \
	mkdir /home/owner && \
	tar xf /home/home.tar -C /home/owner && \
	chown -R owner:users /home/owner && \
	rm /home/home.tar && \
	echo "owner ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Configure start
COPY files/docker-init /etc/
ENV DESKTOP_SESSION=xfce
EXPOSE 22
ENTRYPOINT ["/tini", "/etc/docker-init"]
