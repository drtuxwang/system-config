IMAGE := debian-builder
CPUSHARE := --cpu-shares=100000 --cpu-quota=1000000
MEMLIMIT :=  -memory-reservation=64m --memory=1024m

default: build

build:
	@echo "\n*** Building Docker image ***"
	docker build -t $(IMAGE) .
	docker images

run:
	@echo "\n*** Running Docker container ***"
	docker run $(CPUSHARE) $(MEMLIMIT) \
		--rm \
		--interactive \
		--tty \
		--volume="/etc/passwd:/etc/passwd:ro" \
		--volume="/etc/group:/etc/group:ro" \
		--volume=/shared:/shared \
		--env USER=$(USER) \
		--name $(IMAGE) \
		--hostname $(IMAGE) \
		$(IMAGE) /etc/docker-init || exit 0
