FROM drtuxwang/centos-base:6

# Install sandbox environment packages
RUN yum -y install mesa-libGL SDL tmux wget xorg-x11-server-utils xorg-x11-xauth &&\
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
		libsqlite3x-devel \
		ncurses-devel \
		openssl-devel \
		readline-devel \
		tk-devel \
		xz-devel && \
	yum clean all

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
COPY tmpdir/etc/docker-xinit /etc/
ENTRYPOINT ["/etc/docker-xinit"]
