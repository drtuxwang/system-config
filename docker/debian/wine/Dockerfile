FROM drtuxwang/debian-xbase:9

# Install WINE packages
RUN dpkg --add-architecture i386 && \
	sed -i "s/^deb http/deb [arch=amd64,i386] http/" /etc/apt/sources.list && \
	apt-get update && \
	apt-get install --no-install-recommends -y wine wine64 wine32:i386 && \
	apt-get clean

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
