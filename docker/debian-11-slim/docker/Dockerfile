ARG BASE_IMAGE=drtuxwang/debian:latest

FROM ${BASE_IMAGE}

ARG DOCKER_REPO=None
ARG DOCKER_DEB=None

RUN wget --progress=bar:force $DOCKER_REPO/$DOCKER_DEB && \
    dpkg -i $DOCKER_DEB && \
    rm $DOCKER_DEB

ADD tmpdir/root.tar /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
