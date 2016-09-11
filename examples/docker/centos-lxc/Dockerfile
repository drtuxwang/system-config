FROM centos:7

# Install packages
RUN yum -y update && \
    yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
    yum -y install net-tools sudo vim wget && \
    yum -y install xorg-x11-server-utils xorg-x11-utils alsa-lib && \
    yum -y install python34 && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py
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
