ARG BASE_IMAGE=drtuxwang/python:latest

FROM ${BASE_IMAGE}

RUN python3 -m pip install setuptools==80.10.2 && \
    python3 -m pip install \
        devpi-server==6.18.0 \
        devpi-web==4.2.3 \
        devpi-common==4.0.4 && \
    devpi-init --serverdir=/var/lib/devpi && \
    devpi-gen-secret --secretfile=/var/lib/devpi/.secret

# Configure start
ENV PYTHONDONTWRITEBYTECODE=1
EXPOSE 8080
ENTRYPOINT ["devpi-server"]
CMD ["--serverdir=/var/lib/devpi", "--secretfile=/var/lib/devpi/.secret", "--host=0.0.0.0", "--port=8080"]
