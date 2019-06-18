FROM drtuxwang/python

##RUN python3 -m pip install devpi-server devpi-web && \
##	devpi-server --init --serverdir=/var/lib/devpi
RUN python3 -m pip install devpi-server devpi-web && \
	devpi-server --init --serverdir=/var/lib/devpi

# Configure start
ENV PYTHONDONTWRITEBYTECODE 1
EXPOSE 8080
ENTRYPOINT ["devpi-server", "--serverdir=/var/lib/devpi", "--host=0.0.0.0", "--port=8080"]
