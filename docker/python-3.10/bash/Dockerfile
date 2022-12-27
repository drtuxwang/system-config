ARG BASE_IMAGE=drtuxwang/python:latest

FROM ${BASE_IMAGE}

COPY rootfs/ /

# Configure start
ENV HOME=/root
WORKDIR /root
ENTRYPOINT ["bash", "-l"]
