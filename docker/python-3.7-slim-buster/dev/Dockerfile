ARG BASE_IMAGE=drtuxwang/python:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
RUN apt-get install --no-install-recommends -y \
		g++ \
		libcurl4-openssl-dev \
		libssl-dev && \
	apt-get clean

# Install Python packages
COPY tmpdir/etc/install-python-requirements.sh tmpdir/etc/python-requirements.txt /etc/
RUN /etc/install-python-requirements.sh /usr/local/bin/python3 && \
	rm -f /etc/install-python-requirements.sh /etc/python-requirements.txt

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
