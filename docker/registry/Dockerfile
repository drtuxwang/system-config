ARG BASE_IMAGE=registry:latest

FROM ${BASE_IMAGE}

COPY ./files/config.yml /etc/docker/registry/

# Fix bash
COPY files/ash2bash /bin/bash
RUN ln -s .bashrc /root/.profile

# Root account
COPY tmpdir/root/.??* /root/

# Configure start
ENV REGISTRY_STORAGE_DELETE_ENABLED=true
EXPOSE 5000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/etc/docker/registry/config.yml"]
