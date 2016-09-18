FROM debian-lxc

# Install packages
RUN apt-get install -y openvpn
RUN apt-get install -y resolvconf || exit 0

# Docker OpenVPN startup file
COPY config/docker-openvpn-init /etc/docker-openvpn-init

# Run "/etc/docker-openvpn-init" script
CMD /etc/docker-openvpn-init
