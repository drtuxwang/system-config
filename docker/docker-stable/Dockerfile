ARG BASE_IMAGE=docker:latest

FROM ${BASE_IMAGE}

# Fix bash
COPY files/ash2bash /bin/bash
RUN ln -s .bashrc /root/.profile

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
