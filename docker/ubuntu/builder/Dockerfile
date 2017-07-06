FROM drtuxwang/ubuntu-base:16.04

# Install compiler & dev packages
RUN apt-get install --no-install-recommends -y \
		g++ \
		gfortran && \
	apt-get install --no-install-recommends -y \
		libbz2-dev \
		libdb5.3-dev \
		libreadline6-dev \
		libsqlite3-dev \
		libssl-dev \
		zlib1g-dev && \
	apt-get install --no-install-recommends -y \
		libevent-dev \
		libncurses5-dev && \
	apt-get clean

# Bash shell full setup
COPY tmpdir/bin/ /opt/software/bin/
COPY tmpdir/config/docker-init tmpdir/config/docker-init-home /etc/
COPY tmpdir/config/login /home/docker/.login
COPY tmpdir/config/profile /home/docker/.profile
COPY tmpdir/config/tmux.conf /home/docker/.tmux.conf
COPY tmpdir/config/vimrc /home/docker/.vimrc
ENTRYPOINT ["/etc/docker-init"]
