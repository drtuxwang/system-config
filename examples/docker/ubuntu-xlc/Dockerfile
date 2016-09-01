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
COPY config/bashrc /root/.bashrc
COPY config/vimrc /root/.vimrc

# Create "/home/docker" directory
COPY config/profile /home/docker/.profile
COPY config/terminalrc /home/docker/.config/xfce4/terminal/terminalrc
COPY config/vimrc /home/docker/.vimrc
RUN mkdir -p /home/docker/Desktop && \
    echo "export XDG_CURRENT_DESKTOP=XFCE" > /home/docker/.profile-local

# Set UID script for X-server
COPY config/docker-init /etc/docker-init

# Run "/etc/docker-init" script
USER root
ENV HOME=/root
ENV XDG_CURRENT_DESKTOP=XFCE
WORKDIR /root
CMD /etc/docker-init
