ARG BASE_IMAGE=drtuxwang/python:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
RUN \
	# For Python packages
	apt-get install --no-install-recommends -y g++ libcurl4-openssl-dev libssl-dev make && \
	apt-get clean

# Install Python packages
COPY tmpdir/install-python-requirements.sh tmpdir/python-requirements*.txt* /etc/
RUN /etc/install-python-requirements.sh /usr/local/bin/python3 piponly

ADD tmpdir/root.tar /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
