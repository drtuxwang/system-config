ARG BASE_IMAGE=drtuxwang/debian:latest
ARG USER=owner
ARG GROUP=users

FROM ${BASE_IMAGE} as builder
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

# Install compiler & dev packages
RUN \
    # For Python build
    apt-get install --no-install-recommends --fix-missing -y \
        g++ \
        gfortran \
        libbz2-dev \
        libdb5.3-dev \
        libevent-dev \
        libffi-dev \
        libgdbm-dev \
        liblzma-dev \
        libncurses-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        make \
        python3-dev \
        uuid-dev && \
    # For Python packages
    apt-get install --no-install-recommends --fix-missing -y \
        libcurl4-openssl-dev && \
    apt-get clean

# Install user environment packages
RUN \
    # User environment
    apt-get install --no-install-recommends --fix-missing -y \
        file \
        fonts-noto-cjk \
        fonts-symbola \
        libgl1-mesa-glx \
        libsdl1.2debian \
        openssh-server \
        procps \
        sudo \
        tmux \
        tk \
        x11-xserver-utils \
        xauth && \
    mkdir -p /run/sshd && \
    # XFCE desktop
    apt-get install --no-install-recommends --fix-missing -y \
        xorg \
        dbus-x11 \
        xfce4 \
        xfce4-datetime-plugin \
        xfce4-notifyd \
        xfce4-screenshooter \
        xfce4-terminal && \
    # VNC server
    apt-get install --no-install-recommends --fix-missing -y \
        tigervnc-standalone-server \
        tigervnc-common && \
    # WINE 32bit server
    dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install --no-install-recommends --fix-missing -y \
        wine \
        wine64 \
        wine32:i386 \
        libc6-dev:i386 && \
    apt-get clean && \
    # Init for container
    wget \
        --progress=bar:force \
        https://github.com/krallin/tini/releases/download/v0.19.0/tini-amd64 \
        -O /tini && \
    chmod 755 /tini && \
    # Setup accounts
    useradd --shell /bin/bash --gid ${GROUP} ${USER}

COPY --from=builder /rootfs /
RUN /etc/python-packages.bash -pip /usr/bin/python3 && \
    grep -E "^(bson|dicttoxml|Jinja2|MarkupSafe|pip|python-dateutil|PyYAML|setuptools|six|urllib3|wheel|xmltodict)" \
        /etc/python-requirements.txt > /etc/python-requirements_min.txt && \
    /etc/python-packages.bash /usr/bin/python3 /etc/python-requirements_min.txt && \
    rm /etc/python-requirements_min.txt && \
    chown -R ${USER}:${GROUP} /home/${USER}

# Configure start
ENV DESKTOP_SESSION=xfce
EXPOSE 22
ENTRYPOINT ["/tini", "/etc/docker-init"]
