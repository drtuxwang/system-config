IMAGE := debian-geeqie
CPUSHARE := --cpu-shares=100000 --cpu-quota=1000000
MEMLIMIT :=  -memory-reservation=64m --memory=1024m

default: build

build:
	@echo "\n*** Building Docker image ***"
	cp -rp ../../../../bin ../../../../config .
	bin/fmod -R *
	docker build -t $(IMAGE) .
	rm -rf bin config

	sed -i -e "s/IMAGE=.*/IMAGE=$(IMAGE)/" \
		-e "s/CPUSHARE=.*/CPUSHARE=\"$(CPUSHARE)\"/" \
		-e "s/MEMLIMIT=.*/MEMLIMIT=\"$(MEMLIMIT)\"/" geeqie

	docker images

run:
	./geeqie
