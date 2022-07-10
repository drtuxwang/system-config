ARG BASE_IMAGE=drtuxwang/python:latest

FROM ${BASE_IMAGE}

RUN python3 -m pip install \
        devpi-server==6.5.1 \
        devpi-web==4.0.8 \
        devpi-common==3.6.0 && \
    devpi-init --serverdir=/var/lib/devpi

# Configure start
ENV PYTHONDONTWRITEBYTECODE 1
EXPOSE 8080
ENTRYPOINT ["devpi-server", "--serverdir=/var/lib/devpi", "--host=0.0.0.0", "--port=8080"]
