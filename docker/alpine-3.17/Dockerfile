ARG BASE_IMAGE=alpine:latest

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
        vim
