ARG BASE_IMAGE=drtuxwang/clearlinux:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
# Python missing: _bz2 _dbm _gdbm
RUN swupd bundle-add c-basic \
		make \
		devpkg-ncurses \
		devpkg-openssl \
		devpkg-readline \
		devpkg-sqlite-autoconf \
		devpkg-xz && \
	swupd clean

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
