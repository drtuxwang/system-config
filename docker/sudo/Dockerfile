ARG BASE_IMAGE=scratch

FROM ${BASE_IMAGE}

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
