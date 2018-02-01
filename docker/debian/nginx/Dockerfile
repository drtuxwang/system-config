FROM drtuxwang/debian:latest

RUN apt-get install --no-install-recommends -y nginx-light

# NGINX full setup
# For https use "/etc/ssl/private"
ADD files/nginx-proxy.conf /etc/nginx/conf.d/
EXPOSE 80 443
ENTRYPOINT ["nginx", "-g", "daemon off;"]
