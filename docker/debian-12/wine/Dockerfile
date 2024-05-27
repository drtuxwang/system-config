ARG BASE_IMAGE=debian:latest

FROM ${BASE_IMAGE}

# WINE 32bit server
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install --no-install-recommends --fix-missing -y \
        wine \
        wine64 \
        wine32:i386 \
        libc6-dev:i386 && \
    apt-get clean

ENTRYPOINT ["wine", "cmd"]
