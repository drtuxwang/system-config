FROM k8s.gcr.io/etcd:3.3.17

# Fix bash
COPY files/ash2bash /bin/bash
RUN ln -s .bashrc /root/.profile

# Root account
COPY tmpdir/root/.bashrc /root/

# Configure start
ENV HOME=/root
EXPOSE 2379 2380 4001 7001
WORKDIR /root
