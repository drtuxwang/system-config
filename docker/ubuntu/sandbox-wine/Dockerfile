FROM drtuxwang/ubuntu-sandbox:18.04

# Install WINE packages
RUN dpkg --add-architecture i386 && \
	sed -i "s/^deb http/deb [arch=amd64,i386] http/" /etc/apt/sources.list && \
	apt-get update && \
	apt-get install --no-install-recommends -y wine-stable wine32 wine64 x11-xserver-utils && \
	apt-get clean && \
	winecfg && \
	tar cf /home/home-wine.tar -C /root .wine && \
	rm -rf /root/.??*

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Add home directory archive
COPY tmpdir/home.tar /home/

# Configure start
COPY tmpdir/etc/docker-init /etc/
ENTRYPOINT ["/tini", "/etc/docker-init"]
