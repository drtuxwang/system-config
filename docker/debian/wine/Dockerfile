FROM drtuxwang/debian-xfce:latest

# Install WINE packages
RUN dpkg --add-architecture i386 && \
	sed -i "s/^deb http/deb [arch=amd64,i386] http/" /etc/apt/sources.list && \
	apt-get update && \
	apt-get install --no-install-recommends -y wine wine32 wine64 && \
	apt-get clean
