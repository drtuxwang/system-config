FROM debian:8

# Install packages
RUN apt-get update && apt-get install -y net-tools sudo vim wget
RUN apt-get install -y x11-xserver-utils xterm
RUN apt-get install -y python3 python3-dev python3-pip
RUN apt-get install -y python python-dev python-pip
RUN python3 -m pip install pep8 pylint
RUN python -m pip install pep8 pylint

# Python scripts
COPY bashrc /root/.bashrc
COPY bin /opt/software/bin

# Create docker user account
RUN echo "docker:x:1000:100:Docker User:/home/docker:/bin/bash" >> /etc/passwd
RUN echo "docker ALL=(ALL) NOPASSWD: ALL\nDefaults umask = 0022\nDefaults umask_override" \
    >> /etc/sudoers.d/docker

# Create "/home/docker"
RUN mkdir -p /home/docker/Desktop
COPY profile /home/docker/.profile
COPY vimrc /home/docker/.vimrc
RUN chown -R 1000:100 /home/docker

# Set UID script for X-server
COPY files/docker-setuid /etc/docker-setuid

# Run using docker user account
USER docker
ENV HOME /home/docker
WORKDIR /home/docker
CMD bash -l
