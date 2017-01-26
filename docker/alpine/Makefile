IMAGE := alpine-dock
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=1024m \
	--name $(IMAGE) \
	--hostname $(IMAGE)


default: build

build:
	@echo "\n*** Building Docker image ***"
	mkdir tmpdir ||:
	cp -rp ../../bin ../../config tmpdir
	tmpdir/bin/fmod -R *
	docker build -t $(IMAGE) .
	rm -rf tmpdir
	docker images

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

run:
	@echo "\n*** Running Docker container ***"
	docker run $(FLAGS) $(IMAGE) bash || exit 0
