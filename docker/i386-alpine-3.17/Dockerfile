ARG BASE_IMAGE=i386/alpine:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN apk update && \
    apk add \
        bash \
        bind-tools \
        curl \
        iproute2 \
        openssh-client \
        python3 \
        socat \
        tcptraceroute \
        vim && \
    echo -e '#!/bin/bash\n/bin/uname "$@" | sed -e "s/x86_64/i386/g"' > /usr/local/bin/uname && \
    chmod ugo+rx /usr/local/bin/uname
