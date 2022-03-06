ARG BASE_IMAGE=drtuxwang/alpine-i386:latest

FROM ${BASE_IMAGE}

COPY root-disk/ /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
