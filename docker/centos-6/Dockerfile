FROM centos:6

# Install base packages
RUN yum -y install epel-release && \
	yum -y update && \
	yum -y install net-tools openssh-clients pciutils python34 vim && \
	curl https://bootstrap.pypa.io/get-pip.py | python3.4 && \
	python3 -m pip install --upgrade pip

# Root account
COPY tmpdir/config/.bashrc tmpdir/config/.vimrc /root/

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
