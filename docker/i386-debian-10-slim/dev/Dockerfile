ARG BASE_IMAGE=drtuxwang/i386-debian:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
RUN \
	# For Python build
	apt-get install --no-install-recommends -y \
		g++ \
		gfortran \
		libbz2-dev \
		libdb5.3-dev \
		libevent-dev \
		libffi-dev \
		libgdbm-dev \
		liblzma-dev \
		libncurses5-dev \
		libreadline6-dev \
		libsqlite3-dev \
		libssl-dev \
		python3-dev \
		uuid-dev && \
	# For Python packages
	apt-get install --no-install-recommends -y libcurl4-openssl-dev make && \
	apt-get clean

# Install Python packages
COPY tmpdir/etc/install-python-requirements.sh tmpdir/etc/python-requirements*.txt /etc/
RUN /etc/install-python-requirements.sh /usr/bin/python3 piponly && \
	apt-get clean

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
