IMAGE := wnameless/oracle-xe-11g
HOSTNAME := oracle-dock
FLAGS := --rm \
	--privileged=true \
	--interactive \
	--tty \
	--cpu-period=100000 \
	--cpu-shares=100000 \
	--cpu-quota=1000000 \
	--memory-reservation=64m \
	--memory=2048m \
	--publish 1521:1521 \
	--name $(HOSTNAME) \
	--hostname $(HOSTNAME)


default: run

clean:
	docker rmi -f $(IMAGE) ||:

pull:
	docker pull $(IMAGE)

run:
	@echo "\n*** Running \"$(IMAGE)\" Docker container ***"
	docker run $(FLAGS) $(IMAGE) || exit 0
