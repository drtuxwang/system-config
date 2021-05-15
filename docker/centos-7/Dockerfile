ARG BASE_IMAGE=centos:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN yum -y install epel-release && \
	yum -y update && \
	yum -y install \
		bind-utils \
		iproute \
		net-tools \
		openssh-clients \
		pciutils \
		python36 \
		socat \
		vim \
		wget && \
	rpm -e --nodeps python3-pip python3-setuptools && \
	yum clean all && \
	rm -rf \
		/root/.bash_logout \
		/root/.bash_profile \
		/root/.cache \
		/root/.cshrc \
		/root/.pki \
		/root/.tcshrc \
		/root/anaconda-ks.cfg
