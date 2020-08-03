ARG BASE_IMAGE=drtuxwang/alpine-i386:latest

FROM ${BASE_IMAGE}

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
