default: build

build:
	@echo "\n*** Building Docker image ***"
	rm -rf tmpdir
	mkdir tmpdir
	cp -rp ../../../bin tmpdir
	tmpdir/bin/fmod tmpdir/bin/*
	cp -p ../../../config/profile ../../../config/vimrc tmpdir
	docker build -t centos-7-lxc .
	docker images
	rm -rf tmpdir

run:
	@echo "\n*** Running Docker container ***"
	docker run --interactive --tty --memory=1024mb \
		--name centos-7-lxc --hostname centos-7-lxc --rm centos-7-lxc

xrun:
	@echo "\n*** Running Docker container ***"
	docker run --interactive --tty --memory=1024mb \
		--env DISPLAY=$(DISPLAY) --volume /tmp/.X11-unix:/tmp/.X11-unix \
		--name centos-7-lxc --hostname centos-7-lxc --rm \
		centos-7-lxc /etc/docker-setuid `id -u`
