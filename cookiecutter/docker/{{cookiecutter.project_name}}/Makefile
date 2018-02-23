NAME := {{ cookiecutter.image_name }}
VERSION = {{ cookiecutter.image_version }}
IMAGE := drtuxwang/$(NAME):$(VERSION)
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-shares=50mi \
	--cpu-quota=1000mi \
	--memory-reservation=50m \
	--memory=1000m


default: build
	docker images

clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build:
	mkdir tmpdir ||: && cp -rp ../../bin ../../config tmpdir && tmpdir/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	rm -rf tmpdir

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		--name $(NAME) \
		--hostname $(NAME) \
		$(IMAGE) bash || exit 0
