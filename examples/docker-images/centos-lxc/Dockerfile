FROM centos:7

# Install packages
RUN yum -y update && \
    yum -y install net-tools sudo vim wget && \
    yum -y install xorg-x11-server-utils xorg-x11-utils xterm && \
    yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
    yum -y install python34 && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py && \
    yum -y install python-pip.noarch
RUN python3 -m pip install pep8 pylint && \
    python -m pip install pep8 pylint

# Python scripts
COPY bin /opt/software/bin

# Root setup
COPY bashrc /root/.bashrc
COPY vimrc /root/.vimrc

# Create "/home/docker" directory
RUN mkdir -p /home/docker/Desktop
COPY profile /home/docker/.profile
COPY vimrc /home/docker/.vimrc

# Set UID script for X-server
COPY docker-init /etc/docker-init

# Run "/etc/docker-init" script
USER root
ENV HOME /root
WORKDIR /root
CMD /etc/docker-init
