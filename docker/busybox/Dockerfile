FROM busybox:1.28

# Root account
COPY tmpdir/config/.bashrc /root/
RUN ln -s .bashrc /root/.profile

# Add scripts
COPY tmpdir/bin/bash /bin/bash
COPY tmpdir/bin/sysinfo.sh /opt/software/bin/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
