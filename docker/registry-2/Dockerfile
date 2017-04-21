FROM registry:2

COPY ./files/config.yml /etc/docker/registry/

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]

ENV REGISTRY_STORAGE_DELETE_ENABLED=true

CMD ["/etc/docker/registry/config.yml"]
