ARG BASE_IMAGE=drtuxwang/debian-dev:latest
ARG USER=owner
ARG GROUP=users

FROM ${BASE_IMAGE} AS builder
ARG USER
ARG GROUP

RUN mkdir -p /rootfs/home
COPY rootfs/ /rootfs
COPY files/docker-init /etc/

# Create user's home directory
RUN cp -p /rootfs/root/.??* /rootfs/home/${USER} && \
    mkdir /rootfs/home/${USER}/.ssh && \
    chmod 711 /rootfs/home/${USER} && \
    chmod 700 /rootfs/home/${USER}/.ssh

FROM ${BASE_IMAGE}
ARG USER
ARG GROUP

# Install user environment packages
RUN apt-get install --no-install-recommends --fix-missing -y \
        dbus-x11 \
        fonts-noto-cjk \
        fonts-symbola \
        libgl1-mesa-glx \
        libsdl1.2debian \
        x11-xserver-utils \
        xauth \
        xfce4 \
        xfce4-datetime-plugin \
        xfce4-notifyd \
        xfce4-screenshooter \
        xfce4-terminal \
        xorg && \
    apt-get install --no-install-recommends --fix-missing -y \
        file \
        openssh-server \
        procps \
        sudo \
        tigervnc-standalone-server \
        tigervnc-common \
        tk \
        tmux && \
    apt-get clean && \
    mkdir -p /run/sshd && \
    wget \
        --progress=bar:force \
        https://github.com/krallin/tini/releases/download/v0.19.0/tini-amd64 \
        -O /tini && \
    chmod 755 /tini && \
    useradd --shell /bin/bash --gid ${GROUP} ${USER}

# Python installation
COPY --from=builder /rootfs /
RUN apt-get install --no-install-recommends --fix-missing -y \
        python3 \
        python3-dev && \
    apt-get clean && \
    rm /usr/lib/python*/EXTERNALLY-MANAGED && \
    /etc/python-packages.bash -pip -sys /usr/bin/python3 && \
    grep -E "^(bson|dicttoxml|Jinja2|MarkupSafe|packaging|pip|python-dateutil|PyYAML|setuptools|six|urllib3|wheel|xmltodict)" \
        /etc/python-requirements.txt > /etc/python-requirements_min.txt && \
    /etc/python-packages.bash -sys /usr/bin/python3 /etc/python-requirements_min.txt && \
    rm /etc/python-requirements_min.txt && \
    chown -R ${USER}:${GROUP} /home/${USER}

# Configure start
ENV DESKTOP_SESSION=xfce
EXPOSE 22
ENTRYPOINT ["/tini", "/etc/docker-init"]
