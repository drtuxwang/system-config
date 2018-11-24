FROM drtuxwang/centos-base:7

# Install sandbox environment packages
RUN yum -y install mesa-libGL SDL tmux wget xorg-x11-server-utils xorg-x11-xauth && \
	yum clean all

# Install compiler & dev packages
RUN yum -y install \
		gcc-c++ \
		gcc-gfortran \
		make \
		bzip2-devel \
		gdbm-devel \
		libdb-devel \
		libevent-devel \
		libffi-devel \
		libsqlite3x-devel \
		ncurses-devel \
		openssl-devel \
		readline-devel \
		tk-devel \
		uuid-devel \
		xz-devel && \
	yum clean all

# Configure start
RUN wget https://github.com/krallin/tini/releases/download/v0.18.0/tini-amd64 -O /tini && \
	chmod 755 /tini && \
	rm -f /root/.bash_logout /root/.bash_profile
COPY tmpdir/etc/docker-xinit /etc/
ENTRYPOINT ["/tini", "/etc/docker-xinit"]

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/
