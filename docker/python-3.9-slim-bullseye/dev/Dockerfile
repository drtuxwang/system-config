ARG BASE_IMAGE=drtuxwang/python:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
RUN \
    # For Python packages
    apt-get install --no-install-recommends -y g++ libcurl4-openssl-dev libssl-dev make && \
    apt-get clean

# Install Python packages
COPY tmpdir/python-packages.sh tmpdir/python*-requirements.txt /etc/
RUN /etc/python-packages.sh -pip /usr/local/bin/python3

ADD tmpdir/root.tar /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
