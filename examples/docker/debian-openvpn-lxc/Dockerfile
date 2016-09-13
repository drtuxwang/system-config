FROM debian-lxc

# Install packages
RUN apt-get install -y openvpn
RUN apt-get install -y resolvconf || exit 0

# Run "/etc/docker-init" script
CMD /etc/docker-init
