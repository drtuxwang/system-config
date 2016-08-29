FROM centos:7

# Install packages
RUN yum -y update && \
    yum -y install net-tools sudo vim wget && \
    yum -y install xorg-x11-server-utils xorg-x11-utils && \
    yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
    yum -y install xfce4-terminal && \
    yum -y install python34 && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py
RUN python3 -m pip install pep8 pylint

# Python scripts
COPY bin /opt/software/bin

# Root setup
COPY bashrc /root/.bashrc
COPY vimrc /root/.vimrc

# Create "/home/docker" directory
COPY profile /home/docker/.profile
COPY terminalrc /home/docker/.config/xfce4/terminal/terminalrc
COPY vimrc /home/docker/.vimrc
RUN mkdir -p /home/docker/Desktop && \
    echo "export XDG_CURRENT_DESKTOP=XFCE" > /home/docker/.profile-local

# Set UID script for X-server
COPY docker-init /etc/docker-init

# Run "/etc/docker-init" script
USER root
ENV HOME=/root
ENV XDG_CURRENT_DESKTOP=XFCE
WORKDIR /root
CMD /etc/docker-init
