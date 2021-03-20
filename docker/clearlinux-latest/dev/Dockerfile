ARG BASE_IMAGE=drtuxwang/clearlinux:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
# Python missing: _bz2 _dbm _gdbm
RUN \
	# For Python build
	swupd bundle-add \
		c-basic \
		make \
		devpkg-ncurses \
		devpkg-openssl \
		devpkg-readline \
		devpkg-sqlite-autoconf \
		devpkg-xz && \
	# For Python packages
	swupd bundle-add devpkg-curl && \
	swupd clean

# Install Python packages
COPY tmpdir/install-python-requirements.sh tmpdir/python-requirements*.txt* /etc/
RUN /etc/install-python-requirements.sh /usr/bin/python3 piponly

ADD tmpdir/root.tar /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
