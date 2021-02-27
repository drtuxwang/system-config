ARG BASE_IMAGE=alpine:latest

FROM ${BASE_IMAGE}

# Install base packages
RUN apk update && \
	apk add \
		bash \
		bind-tools \
		curl \
		iproute2 \
		openssh-client \
		python3 \
		vim \
		wget && \
	curl https://bootstrap.pypa.io/get-pip.py | python3
