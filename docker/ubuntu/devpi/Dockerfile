FROM drtuxwang/ubuntu-base:18.04

RUN apt-get install --no-install-recommends -y \
		python3-setuptools && \
	python3 -m pip install devpi-server devpi-web && \
	devpi-server --init --serverdir=/var/lib/devpi

# Root account
COPY tmpdir/config/.bashrc tmpdir/config/.vimrc /root/

# Add scripts
COPY tmpdir/bin/ /opt/software/bin/

# Configure start
ENV PYTHONDONTWRITEBYTECODE 1
EXPOSE 8080
ENTRYPOINT ["devpi-server", "--serverdir=/var/lib/devpi", "--host=0.0.0.0", "--port=8080"]
