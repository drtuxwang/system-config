FROM i386/alpine:3.8

# Install base packages
RUN apk update && \
	apk add bash bind-tools openssh-client python3 vim && \
	python3 -m pip install --upgrade pip && \
	echo -e '#!/bin/bash\n/bin/uname "$@" | sed -e "s/x86_64/i386/g"' > /usr/local/bin/uname && \
	chmod ugo+rx /usr/local/bin/uname

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
