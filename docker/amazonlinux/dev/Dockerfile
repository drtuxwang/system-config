FROM drtuxwang/amazonlinux

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
		uuid-devel \
		xz-devel && \
	yum clean all

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
