FROM ubuntu:16.04

# Install base packages
RUN apt-get update && \
    apt-get install --no-install-recommends -y iputils-ping net-tools openssh-client pciutils vim

# Add scripts
COPY tmpdir/bin/sysinfo.sh /opt/software/bin/

# Root account
COPY tmpdir/config/bashrc /root/.bashrc
COPY tmpdir/config/vimrc /root/.vimrc

# Configure start
USER root
ENV HOME=/root
WORKDIR /root
CMD bash
