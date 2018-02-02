FROM drtuxwang/debian:latest

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
	apt-get install --no-install-recommends -y wine wine32 wine64 && \
	apt-get clean

# Install Python 3 packages
COPY tmpdir/etc/python3-requirements.txt python3-requirements.txt
RUN python3 -m pip install $(cat python3-requirements.txt | sed -e "s/>=/==/g") && \
	rm python3-requirements.txt

# Xfce setup
COPY tmpdir/config/terminalrc /home/docker/.config/xfce4/terminal/terminalrc
ENV XDG_CURRENT_DESKTOP=XFCE

# Bash shell setup
COPY tmpdir/config/docker-init tmpdir/config/docker-init-home /etc/
COPY tmpdir/config/login /home/docker/.login
COPY tmpdir/config/profile /home/docker/.profile
COPY tmpdir/config/tmux.conf /home/docker/.tmux.conf
COPY tmpdir/config/vimrc /home/docker/.vimrc
ENTRYPOINT ["/etc/docker-init"]
