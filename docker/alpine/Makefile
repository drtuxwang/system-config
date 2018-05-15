NAME := alpine
VERSION = latest
IMAGE := drtuxwang/$(NAME):$(VERSION)
DEPENDENT_IMAGES := wine
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=1000m \
	--memory-reservation=50m \
	--volume=/shared:/shared
TOPDIR := ../..


default: build
	docker images

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/config
	cp -p $(TOPDIR)/bin/* tmpdir/bin/
	cp -p $(TOPDIR)/config/bashrc tmpdir/config/.bashrc
	cp -p $(TOPDIR)/config/vimrc tmpdir/config/.vimrc
	$(TOPDIR)/bin/fmod -R *
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -t $(IMAGE) .
	rm -rf tmpdir

	for IMAGE in $(DEPENDENT_IMAGES); do \
		make -C $$IMAGE build || exit 1; \
	done

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) --hostname $(NAME) $(IMAGE) ||:

clean:
	docker rmi -f $(IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
