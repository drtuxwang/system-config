FROM alpine:latest

# Install packages
RUN apk update && \
    apk add bash

# Add scripts
COPY bin/sysinfo.sh /opt/software/bin/

# Root account
COPY config/bashrc /root/.bashrc

# Configure start
USER root
ENV HOME=/root
WORKDIR /root
CMD bash
