ARG BASE_IMAGE=drtuxwang/python-dev:latest

FROM ${BASE_IMAGE}

RUN /etc/python-packages.sh /usr/local/bin/python3

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
