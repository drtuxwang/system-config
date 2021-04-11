ARG BASE_IMAGE=golang:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN apk update && \
	apk add bash openssh-client python3 vim

ADD tmpdir/root.tar /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
