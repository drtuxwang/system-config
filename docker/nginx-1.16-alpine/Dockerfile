ARG BASE_IMAGE=nginx:latest

FROM ${BASE_IMAGE}

ADD tmpdir/root.tar /

# Nginx setup
COPY files/nginx-proxy.conf /etc/nginx/conf.d/
RUN mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf-disabled

# Configure start
EXPOSE 80 443
ENTRYPOINT ["nginx", "-g", "daemon off;"]
