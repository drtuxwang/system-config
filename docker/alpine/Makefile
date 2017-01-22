IMAGE := alpine-base
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=1024m


default: build

build:
	@echo "\n*** Building Docker image ***"
	cp -rp ../../bin ../../config .
	bin/fmod -R *
	docker build -t $(IMAGE) .
	rm -rf bin config
	docker images

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

run:
	@echo "\n*** Running Docker container ***"
	docker run $(FLAGS) \
		--name $(IMAGE)-dock \
		--hostname $(IMAGE)-dock \
		$(IMAGE) bash || exit 0
