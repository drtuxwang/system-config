FROM debian-dock:latest

# Install OpenVPN packages
RUN apt-get install --no-install-recommends -y openvpn && \
    apt-get install --no-install-recommends -y resolvconf || exit 0

# Add scripts
COPY tmpdir/config/docker-init-resolvconf /etc/
