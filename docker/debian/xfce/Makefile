NAME := debian-xfce
VERSION = latest
IMAGE := drtuxwang/$(NAME):$(VERSION)
DEPENDENT_IMAGES := openvpn
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=1024m
XFLAGS := \
	--volume=/etc/passwd:/etc/passwd:ro \
	--volume=/etc/group:/etc/group:ro \
	--volume=/shared:/shared \
	--volume=/tmp/.X11-unix:/tmp/.X11-unix \
	--env TERM=$(TERM) \
	--env USER=$(USER) \
	--env DISPLAY=$(DISPLAY)

default: build
	docker images

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build:
	mkdir tmpdir ||: && cp -rp ../../../config ../../../etc tmpdir
	../../../bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	rm -rf tmpdir

	for IMAGE in $(DEPENDENT_IMAGES); do \
		make -C $$IMAGE build || exit 1; \
	done

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) $(XFLAGS) \
		--hostname $(NAME) \
		$(IMAGE) || exit 0

run-offline:
	@echo "\n*** Running \"$(IMAGE)\" Docker container (offline) ***"
	docker run $(FLAGS) $(XFLAGS) \
		--network none \
		--hostname $(NAME)-offline \
		$(IMAGE) || exit 0

clean:
	for IMAGE in $(DEPENDENT_IMAGES); do \
		make -C $$IMAGE clean; \
	done
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
