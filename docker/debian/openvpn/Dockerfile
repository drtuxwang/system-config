FROM drtuxwang/debian-xfce:latest

# Install OpenVPN packages
RUN apt-get install --no-install-recommends -y openvpn && \
	apt-get clean

# Add scripts
COPY tmpdir/config/docker-init-resolvconf /etc/
