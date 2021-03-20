ARG BASE_IMAGE=registry:latest

FROM ${BASE_IMAGE}

COPY ./files/config.yml /etc/docker/registry/

ADD tmpdir/root.tar /

# Configure start
ENV REGISTRY_STORAGE_DELETE_ENABLED=true
EXPOSE 5000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/etc/docker/registry/config.yml"]
