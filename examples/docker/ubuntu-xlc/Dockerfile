FROM ubuntu:16.04

# Install packages
RUN apt-get update && \
    apt-get install -y net-tools sudo vim wget && \
    apt-get install -y x11-xserver-utils xfce4-terminal && \
    apt-get install -y python3 python3-dev python3-pip
RUN python3 -m pip install pep8 pylint

# Python scripts
COPY bin /opt/software/bin

# Root setup
COPY bashrc /root/.bashrc
COPY vimrc /root/.vimrc

# Create "/home/docker" directory
RUN mkdir -p /home/docker/Desktop
COPY profile /home/docker/.profile
COPY terminalrc /home/docker/.config/xfce4/terminal/terminalrc
COPY vimrc /home/docker/.vimrc

# Set UID script for X-server
COPY docker-init /etc/docker-init

# Run "/etc/docker-init" script
USER root
ENV HOME /root
WORKDIR /root
CMD /etc/docker-init
