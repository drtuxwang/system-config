ARG BASE_IMAGE=docker:latest

FROM ${BASE_IMAGE}

ADD tmpdir/root.tar /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
