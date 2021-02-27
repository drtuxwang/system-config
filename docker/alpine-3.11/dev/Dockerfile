ARG BASE_IMAGE=drtuxwang/alpine:latest

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
		db-dev \
		gdbm-dev \
		libevent-dev \
		libffi-dev \
		ncurses-dev \
		openssl-dev \
		py3-setuptools \
		python3-dev \
		readline-dev \
		sqlite-dev \
		xz-dev && \
	# For Python packages
	apk add \
		blas-dev \
		curl-dev \
		jpeg-dev \
		lapack-dev

# Install Python packages
COPY tmpdir/etc/install-python-requirements.sh tmpdir/etc/python-requirements*.txt /etc/
##RUN /etc/install-python-requirements.sh /usr/bin/python3 && \
##	rm -f /etc/install-python-requirements.sh /etc/python-requirements*.txt

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
