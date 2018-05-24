FROM drtuxwang/centos-base:6

# Root account
COPY tmpdir/config/.bashrc tmpdir/config/.vimrc /root/

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
