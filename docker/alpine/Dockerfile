FROM alpine:3.4

# Install packages
RUN apk update && \
    apk add bash openssh-client vim

# Add scripts
COPY bin/sysinfo.sh /opt/software/bin/

# Root account
COPY config/bashrc /root/.bashrc

# Configure start
USER root
ENV HOME=/root
WORKDIR /root
CMD bash
