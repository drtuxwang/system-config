FROM debian-base-xshell

# Install packages
RUN apt-get install -y openvpn && \
    apt-get install -y resolvconf || exit 0

# Add scripts
COPY config/docker-init-resolvconf /etc/
