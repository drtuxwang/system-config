FROM drtuxwang/debian-xfce:7

# Install compiler packages (Fortran needed by OpenMPI)
RUN apt-get install --no-install-recommends -y \
	g++ \
	gfortran

# Install Dev packages (building Python)
RUN apt-get install --no-install-recommends -y \
	libbz2-dev \
	libdb5.1-dev \
	libreadline6-dev \
	libsqlite3-dev \
	libssl-dev \
	zlib1g-dev

# Install Dev packages (building TMUX)
RUN apt-get install --no-install-recommends -y \
	libevent-dev \
	libncurses5-dev
