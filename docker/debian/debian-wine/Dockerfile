FROM debian-xshell:latest

# Add 32bit
RUN dpkg --add-architecture i386 && \
    sed -i "s/^deb http/deb [arch=amd64,i386] http/" /etc/apt/sources.list && \
    apt-get update

# Install packages
RUN apt-get install --no-install-recommends -y wine64 wine:i386
