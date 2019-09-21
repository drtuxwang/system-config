FROM golang:1.12.9-alpine

# Install base packages
RUN apk update && \
	apk add bash openssh-client python3 vim

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/config/.bashrc tmpdir/config/.vimrc /root/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
