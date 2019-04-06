FROM i386/ubuntu:18.04

# Install base packages
RUN apt-get update --fix-missing && \
	apt-get install --no-install-recommends -y \
		dh-python \
		dnsutils \
		iputils-ping \
		net-tools \
		openssh-client \
		pciutils \
		python3 \
		python3-pip \
		vim && \
	apt-get clean && \
	python3 -m pip install --upgrade pip && \
	echo '#!/bin/bash\n/bin/uname "$@" | sed -e "s/x86_64/i386/g"' > /usr/local/bin/uname && \
	chmod ugo+rx /usr/local/bin/uname && \
	rm -rf /root/.cache
