ARG BASE_IMAGE=drtuxwang/amazonlinux:latest

FROM ${BASE_IMAGE}

ADD tmpdir/root.tar /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
