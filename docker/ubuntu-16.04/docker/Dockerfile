FROM drtuxwang/ubuntu-base:16.04

# Install Docker package (stable instead of latest)
RUN apt-get install --no-install-recommends -y \
		iptables \
		libapparmor1 \
		libdevmapper1.02.1 \
		libltdl7 \
		libseccomp2 \
		wget && \
	wget --progress=bar:force \
		http://apt.dockerproject.org/repo/pool/main/d/docker-engine/docker-engine_1.12.5-0~ubuntu-xenial_amd64.deb && \
	dpkg -i docker-engine_* && \
	dpkg -P wget && \
	rm docker-engine_*

# Root account
COPY tmpdir/config/.bashrc tmpdir/config/.vimrc /root/

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
