FROM drtuxwang/centos-sandbox:7

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
COPY tmpdir/etc/docker-init /etc/
ENTRYPOINT ["/tini", "/etc/docker-init"]

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Add home directory archive

COPY tmpdir/home.tar /home/
