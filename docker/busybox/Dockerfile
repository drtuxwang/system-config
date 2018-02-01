FROM busybox:latest

# Add scripts
COPY tmpdir/bin/sysinfo.sh /opt/software/bin/

# Root account
COPY tmpdir/config/bashrc /root/.bashrc

# Configure start
ENV HOME=/root
WORKDIR /root
CMD busybox sh
