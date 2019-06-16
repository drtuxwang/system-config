FROM drtuxwang/ubuntu

# Install Docker package (stable instead of latest)
RUN apt-get install --no-install-recommends -y \
		iptables \
		libapparmor1 \
		libdevmapper1.02.1 \
		libltdl7 \
		libseccomp2 \
		docker.io

# Root account
COPY tmpdir/config/.bashrc tmpdir/config/.vimrc /root/

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash
