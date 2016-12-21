IMAGE := ubuntu-base
CPUSHARE := --cpu-shares=100000 --cpu-quota=1000000
MEMLIMIT :=  -memory-reservation=64m --memory=1024m

default: build

build:
	@echo "\n*** Building Docker image ***"
	cp -rp ../../../bin ../../../config .
	bin/fmod -R *
	docker build -t $(IMAGE) .
	rm -rf bin config
	docker images

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

run:
	@echo "\n*** Running Docker container ***"
	docker run --cpu-period=100000 $(CPUSHARE) $(MEMLIMIT) \
		--rm \
		--interactive \
		--tty \
		--name $(IMAGE) \
		--hostname $(IMAGE) \
		$(IMAGE) bash || exit 0
