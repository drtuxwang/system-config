ARG BASE_IMAGE=drtuxwang/python:latest

FROM ${BASE_IMAGE}

RUN python3 -m pip install \
		devpi-server==4.7.1 \
		devpi-web==3.4.1 \
		devpi-common==3.3.2 && \
	rm -rf $HOME/.cache && \
	devpi-server --init --serverdir=/var/lib/devpi

# Configure start
ENV PYTHONDONTWRITEBYTECODE 1
EXPOSE 8080
ENTRYPOINT ["devpi-server", "--serverdir=/var/lib/devpi", "--host=0.0.0.0", "--port=8080"]
