FROM debian:8

# Install packages
RUN apt-get update && \
    apt-get install -y net-tools openssh-client pciutils vim

# Add scripts
COPY bin/sysinfo.sh /opt/software/bin/

# Root account
COPY config/bashrc /root/.bashrc
COPY config/vimrc /root/.vimrc

# Configure start
USER root
ENV HOME=/root
WORKDIR /root
CMD bash
