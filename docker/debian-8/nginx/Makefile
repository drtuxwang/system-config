IMAGE := drtuxwang/debian-nginx:8
HOSTNAME := nginx-dock
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=1024m \
	--publish 80:80 \
	--publish 443:443 \
	--name $(HOSTNAME) \
	--hostname $(HOSTNAME)


default: build
	docker images

clean:
	docker rmi -f $(IMAGE) ||:

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build:
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) $(IMAGE) || exit 0
