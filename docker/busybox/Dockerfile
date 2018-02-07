FROM busybox:latest

# Root account
COPY tmpdir/config/.bashrc tmpdir/config/.profile /root/

# Add scripts
COPY tmpdir/bin/sysinfo.sh /opt/software/bin/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD busybox ash -l
