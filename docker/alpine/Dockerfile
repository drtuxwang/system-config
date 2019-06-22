FROM alpine:3.9

# Install base packages
RUN apk update && \
	apk add bash bind-tools openssh-client python3 vim && \
	python3 -m pip install --upgrade pip
