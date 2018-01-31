FROM alpine:3.6

# Install base packages
RUN apk update && \
	apk add bash openssh-client python3 vim

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/config/bashrc /root/.bashrc
COPY tmpdir/config/vimrc /root/.vimrc

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
