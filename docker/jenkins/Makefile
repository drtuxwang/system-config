IMAGE := jenkins
HOSTNAME := jenkins-dock
FLAGS := --rm \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=2048m \
	--volume=/var/lib/jenkins:/var/lib/jenkins \
	--publish 8080:8080 \
	--name $(HOSTNAME) \
	--hostname $(HOSTNAME)


default:

clean:
	docker rmi -f $(IMAGE) ||:

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) $(IMAGE) || exit 0
