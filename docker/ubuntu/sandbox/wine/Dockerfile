FROM drtuxwang/ubuntu-sandbox:18.04

# Install WINE packages
RUN dpkg --add-architecture i386 && \
	sed -i "s/^deb http/deb [arch=amd64,i386] http/" /etc/apt/sources.list && \
	apt-get update && \
	apt-get install --no-install-recommends -y wine-stable wine32 wine64 x11-xserver-utils && \
	apt-get clean && \
	mkdir /root && \
	winecfg && \
	tar cf /home/home-wine.tar -C /root .wine && \
	rm -rf /root/
