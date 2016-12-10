FROM centos:7

# Install packages
RUN yum -y update && \
    yum -y install net-tools openssh-clients pciutils vim

# Add scripts
COPY bin/sysinfo.sh /opt/software/bin/

# Root account
COPY config/bashrc /root/.bashrc
COPY config/vimrc /root/.vimrc

# Configure start
USER root
ENV HOME=/root
WORKDIR /root
CMD bash -l
