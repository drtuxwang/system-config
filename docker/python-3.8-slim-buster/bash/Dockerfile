ARG BASE_IMAGE=drtuxwang/python:latest

FROM ${BASE_IMAGE}

ADD tmpdir/root.tar /

# Configure start
ENV HOME=/root
WORKDIR /root
ENTRYPOINT ["bash", "-l"]
