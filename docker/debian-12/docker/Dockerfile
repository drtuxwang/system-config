ARG BASE_IMAGE=drtuxwang/debian:latest
ARG DOCKER_REPO=None
ARG DOCKER_DEB=None

FROM ${BASE_IMAGE}
ARG DOCKER_REPO
ARG DOCKER_DEB

RUN apt-get install --no-install-recommends -y make && \
    apt-get clean && \
    wget --progress=bar:force $DOCKER_REPO/$DOCKER_DEB && \
    dpkg -i $DOCKER_DEB && \
    rm $DOCKER_DEB

COPY rootfs/ /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
