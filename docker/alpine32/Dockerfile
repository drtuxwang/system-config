FROM i386/alpine:3.9

# Install base packages
RUN apk update && \
	apk add bash bind-tools curl iproute2 openssh-client python3 vim wget && \
	echo -e '#!/bin/bash\n/bin/uname "$@" | sed -e "s/x86_64/i386/g"' > /usr/local/bin/uname && \
	chmod ugo+rx /usr/local/bin/uname
