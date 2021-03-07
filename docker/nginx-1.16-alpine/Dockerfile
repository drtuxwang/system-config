ARG BASE_IMAGE=nginx:latest

FROM ${BASE_IMAGE}

# Fix bash
COPY files/ash2bash /bin/bash
RUN ln -s .bashrc /root/.profile

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Root account
COPY tmpdir/root/.??* /root/

# Nginx setup
COPY files/nginx-proxy.conf /etc/nginx/conf.d/
RUN mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf-disabled

# Configure start
EXPOSE 80 443
ENTRYPOINT ["nginx", "-g", "daemon off;"]
