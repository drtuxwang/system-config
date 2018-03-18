NAME := ubuntu-nginx
VERSION = latest
IMAGE := drtuxwang/$(NAME):$(VERSION)
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=1000m \
	--memory-reservation=50m \
	--volume=/shared:/shared


default: build
	docker images

build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/config
	cp -p ../../../bin/* tmpdir/bin/
	cp -p ../../../config/bashrc tmpdir/config/.bashrc
	cp -p ../../../config/vimrc tmpdir/config/.vimrc
	../../../bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	rm -rf tmpdir

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		--publish 8080:80 \
		--hostname $(NAME) \
		--workdir /var/lib/nginx \
		$(IMAGE) || exit 0

clean:
	docker rmi -f $(IMAGE) ||:
