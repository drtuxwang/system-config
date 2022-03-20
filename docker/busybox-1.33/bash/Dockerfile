ARG BASE_IMAGE=drtuxwang/busybox:latest

FROM ${BASE_IMAGE}

COPY rootfs/ /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
