IMAGE := alpine-docker
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=1024m \
	--volume /var/run/docker.sock:/var/run/docker.sock \
	--privileged=true \
	--name $(IMAGE)-dock \
	--hostname $(IMAGE)-dock


default: build
	docker images

build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) $(IMAGE) bash || exit 0
