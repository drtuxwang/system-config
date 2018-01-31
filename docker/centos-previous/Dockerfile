FROM centos:6

# Install base packages
RUN yum -y install epel-release && \
	yum -y update && \
	yum -y install net-tools openssh-clients pciutils python34 vim && \
	curl https://bootstrap.pypa.io/get-pip.py | python3.4

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/config/bashrc /root/.bashrc
COPY tmpdir/config/vimrc /root/.vimrc

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
