FROM centos:7

# Install packages
RUN yum -y update && \
    yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
    yum -y install gcc net-tools openssh-clients sudo tcsh vim wget && \
    yum -y install xorg-x11-server-utils xorg-x11-utils && \
    yum -y install xfce4-terminal alsa-lib && \
    yum -y install python34 python34-devel && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3 get-pip.py && \
    rm get-pip.py
RUN python3 -m pip install Glances pep8 pylint

# Python scripts
COPY bin /opt/software/bin

# Root setup
COPY config/bashrc /root/.bashrc
COPY config/vimrc /root/.vimrc

# Create "/home/docker" directory
COPY config/profile /home/docker/.profile
COPY config/login /home/docker/.login
COPY config/terminalrc /home/docker/.config/xfce4/terminal/terminalrc
COPY config/vimrc /home/docker/.vimrc

# Docker startup file
COPY config/docker-init /etc/docker-init
COPY config/docker-init-adduser /etc/docker-init-adduser

# Run "/etc/docker-init" script
USER root
ENV HOME=/root
ENV XDG_CURRENT_DESKTOP=XFCE
WORKDIR /root
CMD /etc/docker-init
