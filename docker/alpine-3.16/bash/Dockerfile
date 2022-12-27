ARG BASE_IMAGE=drtuxwang/alpine:latest

FROM ${BASE_IMAGE}

COPY rootfs/ /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
