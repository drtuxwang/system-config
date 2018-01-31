FROM clearlinux:latest

# Install base packages
RUN swupd bundle-add network-basic editors

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/config/bashrc /root/.bashrc
COPY tmpdir/config/vimrc /root/.vimrc

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
