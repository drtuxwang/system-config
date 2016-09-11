FROM centos:7

# Install packages
RUN yum -y update && \
    yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
    yum -y install net-tools sudo vim wget && \
    yum -y install xorg-x11-server-utils xorg-x11-utils xfce4-terminal alsa-lib && \
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
