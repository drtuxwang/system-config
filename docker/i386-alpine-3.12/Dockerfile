ARG BASE_IMAGE=i386/alpine:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN apk update && \
	apk add bash bind-tools curl iproute2 openssh-client python3 py3-pip vim wget && \
	echo -e '#!/bin/bash\n/bin/uname "$@" | sed -e "s/x86_64/i386/g"' > /usr/local/bin/uname && \
	chmod ugo+rx /usr/local/bin/uname
