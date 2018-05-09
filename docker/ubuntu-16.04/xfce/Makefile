NAME := ubuntu
VERSION = 16.04
XBASE_IMAGE := drtuxwang/$(NAME)-xbase:$(VERSION)
IMAGE := drtuxwang/$(NAME)-xfce:$(VERSION)
DEPENDENT_IMAGES := openvpn
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-quota=1000000 \
	--cpu-shares=50000 \
	--memory=2000m \
	--memory-reservation=50m \
	--volume=/etc/passwd:/etc/passwd:ro \
	--volume=/etc/group:/etc/group:ro \
	--volume=/shared:/shared \
	--volume=/tmp/.X11-unix:/tmp/.X11-unix \
	--env TERM=$(TERM) \
	--env USER=$(USER) \
	--env DISPLAY=$(DISPLAY)
TOPDIR := ../../..


default: build
	docker images

pull:
	docker pull `grep FROM Dockerfile | cut -f2 -d" "`

build:
	rm -rf tmpdir
	mkdir -p tmpdir/bin tmpdir/config tmpdir/etc
	cp -p $(TOPDIR)/bin/* tmpdir/bin/
	cp -p $(TOPDIR)/config/bashrc tmpdir/config/.bashrc
	cp -p $(TOPDIR)/config/docker-init $(TOPDIR)/config/docker-init-home tmpdir/config/
	cp -p $(TOPDIR)/config/login tmpdir/config/.login
	cp -p $(TOPDIR)/config/profile tmpdir/config/.profile
	cp -p $(TOPDIR)/config/terminalrc tmpdir/config/
	cp -p $(TOPDIR)/config/tmux.conf tmpdir/config/.tmux.conf
	cp -p $(TOPDIR)/config/vimrc tmpdir/config/.vimrc
	cp -p $(TOPDIR)/etc/python-requirements.txt tmpdir/etc/
	$(TOPDIR)/bin/fmod -R *
	@echo "\n*** Building \"$(XBASE_IMAGE)\" Docker image ***"
	docker build -f Dockerfile -t $(XBASE_IMAGE) .
	@echo "\n*** Building \"$(IMAGE)\" Docker image ***"
	docker build -f Dockerfile2 -t $(IMAGE) .
	rm -rf tmpdir

	for IMAGE in $(DEPENDENT_IMAGES); do \
		make -C $$IMAGE build || exit 1; \
	done

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) --hostname $(NAME) $(IMAGE) || exit 0

run-offline:
	@echo "\n*** Running \"$(IMAGE)\" Docker container (offline) ***"
	docker run $(FLAGS) --network none --hostname $(NAME)-offline $(IMAGE) || exit 0

clean:
	for IMAGE in $(DEPENDENT_IMAGES); do \
		make -C $$IMAGE clean; \
	done
	docker rmi -f $(IMAGE) $(XBASE_IMAGE) ||:
	docker rmi -f `grep FROM Dockerfile | cut -f2 -d" "` ||:
