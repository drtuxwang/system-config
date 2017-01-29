FROM centos:7

# Install base packages
RUN yum -y update && \
	yum -y install net-tools openssh-clients pciutils vim

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
