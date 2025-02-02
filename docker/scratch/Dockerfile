ARG BASE_IMAGE=scratch

FROM ${BASE_IMAGE}

COPY rootfs/ /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD ["bash", "-l"]
