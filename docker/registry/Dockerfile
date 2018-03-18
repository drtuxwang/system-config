FROM registry:2.6

COPY ./files/config.yml /etc/docker/registry/

# Root account
COPY tmpdir/config/.bashrc /root/
RUN ln -s .bashrc /root/.profile

# Add scripts
COPY tmpdir/bin/bash /bin/bash

# Configure start
ENV REGISTRY_STORAGE_DELETE_ENABLED=true
EXPOSE 5000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/etc/docker/registry/config.yml"]
