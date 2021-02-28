ARG BASE_IMAGE=drtuxwang/i386-alpine:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
RUN \
	# For Python build
	apk add \
		gcc \
		g++ \
		gfortran \
		make \
		bzip2-dev \
		curl-dev \
		db-dev \
		gdbm-dev \
		libevent-dev \
		libffi-dev \
		ncurses-dev \
		openssl-dev \
		python3-dev \
		readline-dev \
		sqlite-dev \
		xz-dev && \
	# For Python packages
	apk add blas-dev curl-dev jpeg-dev lapack-dev

# Install Python packages
COPY tmpdir/etc/install-python-requirements.sh tmpdir/etc/python-requirements*.txt /etc/
RUN /etc/install-python-requirements.sh /usr/bin/python3 piponly

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
