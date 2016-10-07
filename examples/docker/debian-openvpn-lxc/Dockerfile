FROM debian-lxc

# Install packages
RUN apt-get install -y openvpn
RUN apt-get install -y resolvconf || exit 0

# Docker OpenVPN startup file
COPY config/docker-init-resolvconf /etc/docker-init-resolvconf
