FROM i386/alpine:3.7

# Install base packages
RUN apk update && \
	apk add bash openssh-client python3 vim && \
	python3 -m pip install --upgrade pip

# 32bit fix
COPY tmpdir/config/docker-uname-i386 /usr/local/bin/uname

# Root account
COPY tmpdir/config/.bashrc tmpdir/config/.vimrc /root/

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
