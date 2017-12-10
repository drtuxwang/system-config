FROM alpine:3.6

# Install base packages
RUN apk update && \
	apk add bash openssh-client vim

# Add scripts
COPY tmpdir/bin/sysinfo.sh /opt/software/bin/

# Root account
COPY tmpdir/config/bashrc /root/.bashrc

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
