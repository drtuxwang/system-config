FROM drtuxwang/ubuntu-base:18.04

RUN apt-get install --no-install-recommends -y nginx-light

# Root account
COPY tmpdir/config/.bashrc tmpdir/config/.vimrc /root/

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# NGINX full setup
# For https use "/etc/ssl/private"
COPY files/nginx-proxy.conf /etc/nginx/conf.d/

# Configure start
EXPOSE 80 443
ENTRYPOINT ["nginx", "-g", "daemon off;"]
