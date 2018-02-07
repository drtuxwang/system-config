FROM alpine:3.6

# Install base packages
RUN apk update && \
	apk add bash openssh-client python3 vim

# Root account
COPY tmpdir/config/.bashrc tmpdir/config/.vimrc /root/

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
