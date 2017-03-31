FROM drtuxwang/debian-xshell

RUN apt-get install --no-install-recommends -y nginx-light

ADD files/nginx-proxy.conf /etc/nginx/conf.d/
## #    --volume="$PWD/config:/etc/ssl/private" \

EXPOSE 80 443

ENTRYPOINT ["nginx", "-g", "daemon off;"]
