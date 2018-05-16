FROM drtuxwang/ubuntu-base:18.04

# Install compiler & dev packages
RUN DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
		g++ \
		gfortran \
		libbz2-dev \
		libdb5.3-dev \
		libevent-dev \
		libgdbm-dev \
		liblzma-dev \
		libncurses5-dev \
		libreadline6-dev \
		libsqlite3-dev \
		libssl-dev \
		python3-dev \
		python3-setuptools \
		tk8.6-dev && \
	apt-get clean

# Install Python 3 packages
COPY tmpdir/etc/python-requirements.txt /root
RUN python3 -m pip install $(cat /root/python-requirements.txt | sed -e "s/>=/==/g") && \
	rm /root/python-requirements.txt

# Root account
COPY tmpdir/config/.bashrc tmpdir/config/.vimrc /root/

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Configure start
COPY tmpdir/config/docker-xinit /etc/
ENTRYPOINT ["/etc/docker-xinit"]
