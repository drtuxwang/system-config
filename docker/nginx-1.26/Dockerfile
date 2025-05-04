ARG BASE_IMAGE=nginx:latest

FROM ${BASE_IMAGE}

COPY rootfs/ /

# Nginx setup
COPY files/nginx-proxy.conf /etc/nginx/conf.d/
RUN mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf-disabled

# Configure start
EXPOSE 80 443
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
