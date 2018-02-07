FROM busybox:latest

# Root account
COPY tmpdir/config/.bashrc /root/

# Add scripts
COPY tmpdir/bin/sysinfo.sh /opt/software/bin/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD busybox sh
