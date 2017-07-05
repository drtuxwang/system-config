NAME := oracle-xe-11g
VERSION = latest
IMAGE := wnameless/$(NAME):$(VERSION)
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=2048m


default: pull

clean:
	docker rmi -f $(IMAGE) ||:

pull:
	docker pull $(IMAGE)

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		--privileged=true \
		--publish 1521:1521 \
		--name $(NAME) \
		--hostname $(NAME) \
		--name $(NAME)-dock \
		--hostname $(NAME)-dock \
		$(IMAGE) || exit 0
