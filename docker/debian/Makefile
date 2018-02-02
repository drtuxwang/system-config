NAME := debian
VERSION = latest
IMAGE := drtuxwang/$(NAME):$(VERSION)
DEPENDENT_IMAGES := devpi docker nginx xfce
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
	mkdir tmpdir ||: && cp -rp ../../bin ../../config tmpdir
	../../bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
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
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
