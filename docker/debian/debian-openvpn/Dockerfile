FROM debian-xshell:latest

# Install packages
RUN apt-get install --no-install-recommends -y openvpn && \
    apt-get install --no-install-recommends -y resolvconf || exit 0

# Add scripts
COPY config/docker-init-resolvconf /etc/
