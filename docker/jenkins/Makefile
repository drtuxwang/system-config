NAME := jenkins
VERSION = latest
IMAGE := $(NAME):$(VERSION)
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=2048m


default:

pull:
	docker pull $(IMAGE)
	docker inspect $(IMAGE) | grep JENKINS_VERSION | uniq

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) \
		--privileged=true \
		--volume=/var/lib/jenkins:/var/lib/jenkins \
		--publish 8080:8080 \
		--hostname $(NAME) \
		$(IMAGE) || exit 0

clean:
	docker rmi -f $(IMAGE) ||:
