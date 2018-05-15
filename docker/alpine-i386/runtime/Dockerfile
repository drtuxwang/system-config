FROM drtuxwang/alpine-i386:latest

# Install base packages
RUN apk update && \
	apk add ttf-freefont xauth xrandr && \
	apk add mesa-gl sdl

# Root account
COPY tmpdir/config/docker-xinit /etc/

# Configure start
WORKDIR /shared
ENTRYPOINT ["/etc/docker-xinit"]
CMD ["bash", "-l"]
