FROM drtuxwang/ubuntu-xbase:latest

# Install OpenVPN packages
RUN apt-get install --no-install-recommends -y openvpn && \
	apt-get clean

# Add scripts
COPY tmpdir/config/docker-init-resolvconf /etc/

# X-windows full setup
COPY tmpdir/config/terminalrc /home/docker/.config/xfce4/terminal/terminalrc
ENV XDG_CURRENT_DESKTOP=XFCE

# Bash shell full setup
COPY tmpdir/bin/ /opt/software/bin/
COPY tmpdir/config/docker-init tmpdir/config/docker-init-home /etc/
COPY tmpdir/config/login /home/docker/.login
COPY tmpdir/config/profile /home/docker/.profile
COPY tmpdir/config/tmux.conf /home/docker/.tmux.conf
COPY tmpdir/config/vimrc /home/docker/.vimrc
ENTRYPOINT ["/etc/docker-init"]
