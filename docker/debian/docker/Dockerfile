FROM debian8-xfce

# Install Docker package (stable instead of latest)
RUN apt-get install --no-install-recommends -y \
		init-system-helpers \
		iptables \
		libapparmor1 \
		libltdl7 && \
	wget --progress=bar:force \
		http://apt.dockerproject.org/repo/pool/main/d/docker-engine/docker-engine_1.12.6-0~debian-jessie_amd64.deb && \
	dpkg -i docker-engine_* && \
	rm docker-engine_*
