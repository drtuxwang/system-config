ARG BASE_IMAGE=golang:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN apk update && \
    apk add bash openssh-client vim && \
    ln -s /usr/local/go/bin/go /usr/local/bin/go

COPY rootfs/ /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD ["bash", "-l"]
