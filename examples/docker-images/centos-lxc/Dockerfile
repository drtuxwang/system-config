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

# Create "owner" user account
RUN echo "owner:x:1000:100:Docker User:/home/owner:/bin/bash" >> /etc/passwd
RUN echo -e "owner ALL=(ALL) NOPASSWD: ALL\nDefaults umask = 0022\nDefaults umask_override" \
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
