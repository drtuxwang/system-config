ARG BASE_IMAGE=drtuxwang/centos:latest

FROM ${BASE_IMAGE}

# Install compiler & dev packages
RUN \
	# For Python build
	yum -y install \
		gcc-c++ \
		gcc-gfortran \
		make \
		bzip2-devel \
		gdbm-devel \
		libdb-devel \
		libcurl-devel \
		libevent-devel \
		libffi-devel \
		libsqlite3x-devel \
		ncurses-devel \
		openssl-devel \
		readline-devel \
		uuid-devel \
		xz-devel && \
	# For Python packages
	yum -y install python36-devel && \
	rpm -e --nodeps python3-rpm-generators python3-rpm-macros python3-setuptools && \
	yum clean all

# Install Python packages
COPY tmpdir/etc/install-python-requirements.sh tmpdir/etc/python-requirements*.txt /etc/
RUN /etc/install-python-requirements.sh /usr/bin/python3 piponly

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
