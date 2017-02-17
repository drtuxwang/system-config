IMAGE_BASE := drtuxwang/debian-base:7
IMAGE_SHELL := drtuxwang/debian-shell:7
HOSTNAME := wheezy-dock
PASSWD := $(HOME)/.docker-passwd
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=1024m \
	--volume=$(PASSWD):/etc/passwd:ro \
	--volume=/etc/group:/etc/group:ro \
	--volume=/shared:/shared \
	--env TERM=$(TERM) \
	--env USER=$(USER) \
	--name $(HOSTNAME) \
	--hostname $(HOSTNAME)


default: build
	docker images

all: build-all
	docker images

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build-all: build
	cd builder && make build

build:
	mkdir tmpdir ||: && cp -rp ../../bin ../../config tmpdir && tmpdir/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE_BASE)\" Docker image ***"
	docker build --force-rm=true -t $(IMAGE_BASE) .
	@echo "\n*** Building \"$(IMAGE_SHELL)\" Docker image ***"
	docker build --force-rm=true -f Dockerfile-shell -t $(IMAGE_SHELL) .
	rm -rf tmpdir

$(PASSWD):
	echo "root:x:0:0:root:/root:/bin/bash\n$(USER):x:`id -u`:`id -g`:-:$(HOME):/bin/bash" > \
	$(HOME)/.docker-passwd

run: $(PASSWD)
	@echo "\n*** Running \"$(IMAGE_SHELL)\" Docker container ***"
	docker run $(FLAGS) $(IMAGE_SHELL) || exit 0
