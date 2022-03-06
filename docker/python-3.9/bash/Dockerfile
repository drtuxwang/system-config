ARG BASE_IMAGE=drtuxwang/python:latest

FROM ${BASE_IMAGE}

COPY root-disk/ /

# Configure start
ENV HOME=/root
WORKDIR /root
ENTRYPOINT ["bash", "-l"]
