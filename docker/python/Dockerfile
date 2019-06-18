FROM python:3.6-alpine

# Fix bash
COPY files/ash2bash /bin/bash
RUN ln -s .bashrc /root/.profile

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
ENV HOME=/root
WORKDIR /root
