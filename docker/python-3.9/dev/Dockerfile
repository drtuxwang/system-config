ARG BASE_IMAGE=drtuxwang/python:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
RUN \
    # For Python packages
    apt-get install --no-install-recommends -y \
        curl \
        g++ \
        libcurl4-openssl-dev \
        libssl-dev \
        make && \
    apt-get clean

COPY rootfs/ /
RUN /etc/python-packages.sh -pip /usr/local/bin/python3

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
