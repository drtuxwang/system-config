FROM drtuxwang/ubuntu-base:16.04

RUN apt-get install --no-install-recommends -y \
		csh \
		ksh \
		sudo \
		tcsh \
		tmux \
		x11-utils \
		x11-xserver-utils \
		xfce4-terminal \
		xfonts-base \
		wget && \
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

# Install WINE packages
RUN dpkg --add-architecture i386 && \
	sed -i "s/^deb http/deb [arch=amd64,i386] http/" /etc/apt/sources.list && \
	apt-get update && \
	apt-get install --no-install-recommends -y wine && \
	apt-get clean

# Install Python 3 packages
COPY tmpdir/etc/python-requirements.txt /root
RUN python3 -m pip install $(cat /root/python-requirements.txt | sed -e "s/>=/==/g") && \
	rm /root/python-requirements.txt

# Xfce setup
COPY tmpdir/config/terminalrc /home/docker/.config/xfce4/terminal/
ENV XDG_CURRENT_DESKTOP=XFCE
