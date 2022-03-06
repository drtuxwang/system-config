ARG BASE_IMAGE=drtuxwang/busybox:latest

FROM ${BASE_IMAGE}

COPY root-disk/ /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
