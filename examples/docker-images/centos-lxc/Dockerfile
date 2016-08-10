FROM centos:7

# Install packages
RUN yum -y update && yum -y install net-tools sudo vim wget
RUN yum -y install xorg-x11-server-utils xorg-x11-utils xterm
RUN yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum -y install python34
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN rm get-pip.py
RUN yum -y install python-pip.noarch
RUN python3 -m pip install pep8 pylint
RUN python -m pip install pep8 pylint

# Python scripts
COPY bashrc /root/.bashrc
COPY bin /opt/software/bin

# Create docker user account
RUN echo "docker:x:1000:100:Docker User:/home/docker:/bin/bash" >> /etc/passwd
RUN echo -e "docker ALL=(ALL) NOPASSWD: ALL\nDefaults umask = 0022\nDefaults umask_override" \
    >> /etc/sudoers.d/docker

# Create "/home/docker"
RUN mkdir -p /home/docker/Desktop
COPY profile /home/docker/.profile
COPY vimrc /home/docker/.vimrc
RUN chown -R 1000:100 /home/docker

# Set UID script for X-server
COPY docker-init /etc/docker-init

# Run using docker user account
USER root
ENV HOME /home/docker
WORKDIR /home/docker
CMD /etc/docker-init
