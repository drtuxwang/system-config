ARG BASE_IMAGE=drtuxwang/alpine:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
RUN apk add gcc \
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
		xz-dev

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
