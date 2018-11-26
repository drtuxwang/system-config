FROM drtuxwang/debian-base:8

# Install sandbox environment packages
RUN apt-get install --no-install-recommends -y \
		file \
		libgl1-mesa-glx \
		libsdl1.2debian \
		tmux \
		wget \
		x11-xserver-utils \
		xauth && \
	apt-get clean

# Install compiler & dev packages
RUN apt-get install --no-install-recommends -y \
		g++ \
		gfortran \
		libbz2-dev \
		libdb5.3-dev \
		libevent-dev \
		libffi-dev \
		libgdbm-dev \
		liblzma-dev \
		libncurses5-dev \
		libreadline6-dev \
		libsqlite3-dev \
		libssl-dev \
		python3-dev \
		tk8.6-dev \
		uuid-dev && \
	apt-get clean

# Configure start
RUN wget https://github.com/krallin/tini/releases/download/v0.18.0/tini-amd64 -O /tini && \
	chmod 755 /tini && \
	rm -f /root/.wget-hsts
COPY tmpdir/etc/docker-init /etc/
ENTRYPOINT ["/tini", "/etc/docker-init"]

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Sandbox account
RUN echo "sandbox:x:99999:99999::/home/sandbox:/bin/bash" >> /etc/passwd && \
	echo "sandbox:x:99999" >> /etc/group && \
	ln -s .profile /root/.bash_profile && \
	touch /root/.bash_logout && \
	chmod 777 /root /home && \
	chmod 666 /root/.??*
