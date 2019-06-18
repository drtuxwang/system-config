FROM nginx:stable-alpine

# Fix bash
COPY files/ash2bash /bin/bash
RUN ln -s .bashrc /root/.profile

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# NGINX full setup
# For https use "/etc/ssl/private"
COPY files/nginx-proxy.conf /etc/nginx/conf.d/

# Configure start
EXPOSE 80 443
ENTRYPOINT ["nginx", "-g", "daemon off;"]
