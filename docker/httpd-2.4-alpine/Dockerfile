ARG BASE_IMAGE=httpd:latest

FROM ${BASE_IMAGE}

ADD tmpdir/root.tar /

# Apache HTTPD setup
COPY files/httpd.conf /usr/local/apache2/conf/httpd.conf
COPY public-html/ /usr/local/apache2/htdocs/

# Configure start
EXPOSE 80
ENTRYPOINT ["httpd-foreground"]
