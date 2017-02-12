FROM drtuxwang/debian-shell

# Install compiler & dev packages
RUN apt-get install --no-install-recommends -y \
		g++ \
		gfortran && \
	apt-get install --no-install-recommends -y \
		libbz2-dev \
		libdb5.3-dev \
		libreadline6-dev \
		libsqlite3-dev \
		libssl-dev \
		zlib1g-dev && \
	apt-get install --no-install-recommends -y \
		libevent-dev \
		libncurses5-dev && \
	apt-get clean
