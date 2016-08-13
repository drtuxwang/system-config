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

# Create "owner" user account
RUN echo "owner:x:1000:100:Docker User:/home/owner:/bin/bash" >> /etc/passwd
RUN echo "owner ALL=(ALL) NOPASSWD: ALL\nDefaults umask = 0022\nDefaults umask_override" \
    >> /etc/sudoers.d/docker

# Create "/home/owner" directory
RUN mkdir -p /home/owner/Desktop
COPY profile /home/owner/.profile
COPY vimrc /home/owner/.vimrc
RUN chown -R 1000:100 /home/owner

# Set UID script for X-server
COPY docker-init /etc/docker-init

# Run "/etc/docker-init" script
USER root
ENV HOME /home/owner
WORKDIR /home/owner
CMD /etc/docker-init
