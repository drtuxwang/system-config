FROM drtuxwang/debian-xfce

# Install OpenVPN packages
RUN apt-get install --no-install-recommends -y openvpn && \
	apt-get install --no-install-recommends -y resolvconf ||: && \
	apt-get clean

# Add scripts
COPY tmpdir/config/docker-init-resolvconf /etc/
