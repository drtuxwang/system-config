FROM drtuxwang/debian-base:8

# Install Docker package (stable instead of latest)
RUN apt-get install --no-install-recommends -y \
		init-system-helpers \
		iptables \
		libapparmor1 \
		libltdl7 && \
	apt-get clean && \
	wget --progress=bar:force \
		http://apt.dockerproject.org/repo/pool/main/d/docker-engine/docker-engine_1.12.6-0~debian-jessie_amd64.deb && \
	dpkg -i docker-engine_* && \
	rm docker-engine_*

# Bash shell full setup
COPY tmpdir/bin/ /opt/software/bin/
COPY tmpdir/config/docker-init tmpdir/config/docker-init-home /etc/
COPY tmpdir/config/login /home/docker/.login
COPY tmpdir/config/profile /home/docker/.profile
COPY tmpdir/config/tmux.conf /home/docker/.tmux.conf
COPY tmpdir/config/vimrc /home/docker/.vimrc
ENTRYPOINT ["/etc/docker-init"]
