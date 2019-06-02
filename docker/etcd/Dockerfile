FROM k8s.gcr.io/etcd:3.3.10

# Root account
COPY tmpdir/config/.bashrc /root/
RUN ln -s .bashrc /root/.profile

# Add scripts
COPY tmpdir/bin/bash /bin/bash
COPY tmpdir/bin/sysinfo.sh /opt/software/bin/

# Configure start
ENV HOME=/root
EXPOSE 2379 2380 4001 7001
WORKDIR /root
CMD bash
