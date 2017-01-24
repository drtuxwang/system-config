FROM debian-shell:latest

# Install compilers (Fortran needed by OpenMPI)
RUN apt-get install --no-install-recommends -y g++ gfortran

# Install packages for building Python
RUN apt-get install --no-install-recommends -y libbz2-dev libdb5.3-dev libreadline6-dev \
    libsqlite3-dev libssl-dev zlib1g-dev

# Install packages for building TMUX
RUN apt-get install --no-install-recommends -y libevent-dev libncurses5-dev
