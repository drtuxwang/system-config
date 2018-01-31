NAME := ubuntu
VERSION = latest
IMAGE := drtuxwang/$(NAME):$(VERSION)
BASE_IMAGE := drtuxwang/$(NAME)-base:$(VERSION)
XBASE_IMAGE := drtuxwang/$(NAME)-xbase:$(VERSION)
DEPENDENT_IMAGES := builder devpi docker nginx openvpn shell wine
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=1024m


default: build
	docker images

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build:
	mkdir tmpdir ||: && cp -rp ../../bin ../../config tmpdir && tmpdir/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	@echo "\n*** Building \"$(BASE_IMAGE)\" Docker image ***"
	docker build -f Dockerfile-base -t $(BASE_IMAGE) .
	@echo "\n*** Building \"$(XBASE_IMAGE)\" Docker image ***"
	docker build -f Dockerfile-xbase -t $(XBASE_IMAGE) .
	rm -rf tmpdir

	for IMAGE in $(DEPENDENT_IMAGES); do \
		make -C $$IMAGE build || exit 1; \
	done

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		--hostname $(NAME) \
		$(IMAGE) || exit 0

clean:
	for IMAGE in $(DEPENDENT_IMAGES); do \
		make -C $$IMAGE clean; \
	done
	docker rmi -f $(IMAGE) $(BASE_IMAGE) $(XBASE_IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
