FROM drtuxwang/ubuntu-sandbox:18.04

# Install WINE packages
RUN apt-get install --no-install-recommends -y firefox fonts-noto-cjk fonts-noto-hinted && \
	apt-get clean

COPY tmpdir/home-firefox.tar /home/
