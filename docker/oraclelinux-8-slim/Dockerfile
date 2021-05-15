ARG BASE_IMAGE=oraclelinux:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN ln -s microdnf /usr/bin/yum && \
	yum -y install oracle-epel-release-el8 && \
	yum -y update && \
	yum -y install \
		bind-utils \
		net-tools \
		openssh-clients \
		pciutils \
		socat \
		python38 \
		vim \
		wget && \
	rpm -e --nodeps \
		platform-python-setuptools \
		python3-pip-wheel \
		python3-setuptools-wheel \
		python38-pip-wheel \
		python38-setuptools-wheel && \
	yum clean all && \
	rm -rf \
		/root/.bash_logout \
		/root/.bash_profile \
		/root/.cache \
		/root/.cshrc \
		/root/.pki \
		/root/.tcshrc \
		/root/anaconda-ks.cfg
