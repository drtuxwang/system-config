ARG BASE_IMAGE=python:latest

FROM ${BASE_IMAGE}


RUN apt-get update --fix-missing && \
	apt-get install --no-install-recommends -y \
		make && \
	apt-get clean
