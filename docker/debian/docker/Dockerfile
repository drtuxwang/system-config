FROM drtuxwang/debian:latest

# Install Docker package (stable instead of latest)
RUN apt-get install --no-install-recommends -y \
		iptables \
		libapparmor1 \
		libdevmapper1.02.1 \
		libltdl7 \
		libseccomp2 \
		wget && \
	wget --progress=bar:force \
		http://apt.dockerproject.org/repo/pool/main/d/docker-engine/docker-engine_1.12.6-0~debian-stretch_amd64.deb && \
	dpkg -i docker-engine_* && \
	dpkg -P wget && \
	rm docker-engine_*
