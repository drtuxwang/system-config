FROM drtuxwang/ubuntu-base:18.04-i386

# Install WINE packages
RUN apt-get install --no-install-recommends -y wine-stable x11-xserver-utils xauth && \
	apt-get clean && \
	winecfg

# Root account
COPY tmpdir/config/.bashrc tmpdir/config/.vimrc /root/

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Configure start
COPY tmpdir/config/docker-xinit /etc/
ENTRYPOINT ["/etc/docker-xinit"]
