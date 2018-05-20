FROM drtuxwang/ubuntu-base:18.04-i386

# Install audio/video packages
RUN apt-get install --no-install-recommends -y \
		libgl1-mesa-glx \
		libsdl1.2debian \
		x11-xserver-utils \
		xauth && \
	apt-get clean

# Root account
COPY tmpdir/config/.bashrc tmpdir/config/.vimrc /root/

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Configure start
COPY tmpdir/config/docker-xinit /etc/
ENTRYPOINT ["/etc/docker-xinit"]
