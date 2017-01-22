IMAGE := debian
PASSWD := $(HOME)/.docker-passwd
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=1024m \
	--volume=/etc/group:/etc/group:ro \
	--volume=$(PASSWD):/etc/passwd:ro \
	--volume=/shared:/shared


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

$(PASSWD):
	echo "root:x:0:0:root:/root:/bin/bash\n$(USER):x:`id -u`:`id -g`:-:$(HOME):/bin/bash" > \
	$(HOME)/.docker-passwd

run: $(PASSWD)
	@echo "\n*** Running Docker container ***"
	docker run $(FLAGS) \
		--env TERM=$(TERM) \
		--env USER=$(USER) \
		--name $(IMAGE)-shell-dock \
		--hostname $(IMAGE)-shell-dock \
		$(IMAGE)-shell /etc/docker-init || exit 0

xrun: $(PASSWD)
	@echo "\n*** Running Docker container (with Graphics)***"
	docker run $(FLAGS) \
		--volume=/tmp/.X11-unix:/tmp/.X11-unix \
		--env DISPLAY=$(DISPLAY) \
		--env TERM=$(TERM) \
		--env USER=$(USER) \
		--name $(IMAGE)-xshell-dock \
		--hostname $(IMAGE)-xshell-dock \
		$(IMAGE)-xshell /etc/docker-init || exit 0
