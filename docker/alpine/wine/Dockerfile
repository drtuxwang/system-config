FROM drtuxwang/alpine:latest

# Install base packages
RUN apk update && \
	apk add ttf-freefont xauth xrandr && \
	apk add wine && \
	winecfg

# Root account
COPY tmpdir/config/docker-xinit /etc/

# Configure start
WORKDIR /shared
ENTRYPOINT ["/etc/docker-xinit"]
CMD ["bash", "-l"]
