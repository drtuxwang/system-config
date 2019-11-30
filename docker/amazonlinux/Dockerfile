FROM amazonlinux:2

# Install base packages
RUN yum -y update && \
	yum -y install bind-utils iproute net-tools openssh-clients pciutils python3 vim wget && \
	yum clean all
