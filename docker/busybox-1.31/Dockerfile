ARG BASE_IMAGE=busybox:latest

FROM ${BASE_IMAGE}

# Fix bash
COPY files/ash2bash /bin/bash
RUN ln -s .bashrc /root/.profile
