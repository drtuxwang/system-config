FROM drtuxwang/ubuntu-base:18.04

# Install WINE packages
RUN dpkg --add-architecture i386 && \
	sed -i "s/^deb http/deb [arch=amd64,i386] http/" /etc/apt/sources.list && \
	apt-get update && \
	apt-get install --no-install-recommends -y wine-stable wine32 wine64 x11-xserver-utils xauth && \
	apt-get clean && \
	winecfg

# Root account
COPY tmpdir/config/.bashrc tmpdir/config/.vimrc /root/

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Configure start
COPY tmpdir/config/docker-xinit /etc/
ENTRYPOINT ["/etc/docker-xinit"]
