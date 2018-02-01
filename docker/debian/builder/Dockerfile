FROM drtuxwang/debian-xfce:latest

# Install compiler & dev packages
RUN apt-get install --no-install-recommends -y \
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
		tk8.6-dev && \
	apt-get clean
