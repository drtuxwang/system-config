IMAGE := drtuxwang/alpine:3.4
HOSTNAME := alpine-dock
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=1024m \
	--name $(HOSTNAME) \
	--hostname $(HOSTNAME)


default: build
	docker images

clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build:
	mkdir tmpdir ||: && cp -rp ../../bin ../../config tmpdir && tmpdir/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	rm -rf tmpdir

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) $(IMAGE) bash || exit 0
