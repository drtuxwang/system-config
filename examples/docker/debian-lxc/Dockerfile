FROM debian:8

# Install packages
RUN apt-get update && \
    apt-get install -y net-tools sudo vim wget && \
    apt-get install -y x11-xserver-utils x11-utils libgtk-3-0 libasound2 && \
    apt-get install -y python3 python3-dev python3-pip
RUN python3 -m pip install pep8 pylint

# Python scripts
COPY bin /opt/software/bin

# Root setup
COPY config/bashrc /root/.bashrc
COPY config/vimrc /root/.vimrc

# Create "/home/docker" directory
COPY config/profile /home/docker/.profile
COPY config/vimrc /home/docker/.vimrc

# Docker startup files
COPY config/docker-init /etc/docker-init
COPY config/docker-exec /etc/docker-exec

# Run "/etc/docker-init" script
USER root
ENV HOME=/root
WORKDIR /root
CMD /etc/docker-init
