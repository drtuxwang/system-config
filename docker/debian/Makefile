IMAGE := debian
CPUSHARE := --cpu-shares=100000 --cpu-quota=1000000
MEMLIMIT :=  -memory-reservation=64m --memory=1024m

default: build

build:
	@echo "\n*** Building Docker image ***"
	cp -rp ../../bin ../../config .
	bin/fmod -R *
	docker build -t $(IMAGE)-base .
	docker build -f Dockerfile-shell -t $(IMAGE)-shell .
	docker build -f Dockerfile-xshell -t $(IMAGE)-xshell .
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
		--volume="/etc/passwd:/etc/passwd:ro" \
		--volume="/etc/group:/etc/group:ro" \
		--volume=/shared:/shared \
		--env USER=$(USER) \
		--env TERM=$(TERM) \
		--name $(IMAGE)-shell \
		--hostname $(IMAGE)-shell \
		$(IMAGE)-shell /etc/docker-init || exit 0

xrun:
	@echo "\n*** Running Docker container ***"
	docker run --cpu-period=100000 $(CPUSHARE) $(MEMLIMIT) \
		--rm \
		--interactive \
		--tty \
		--volume="/etc/passwd:/etc/passwd:ro" \
		--volume="/etc/group:/etc/group:ro" \
		--volume=/tmp/.X11-unix:/tmp/.X11-unix \
		--volume=/shared:/shared \
		--env USER=$(USER) \
		--env TERM=$(TERM) \
		--env DISPLAY=$(DISPLAY) \
		--name $(IMAGE)-xshell \
		--hostname $(IMAGE)-xshell \
		$(IMAGE)-xshell /etc/docker-init || exit 0
