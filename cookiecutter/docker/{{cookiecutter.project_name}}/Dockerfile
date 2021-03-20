ARG BASE_IMAGE={{ cookiecutter.base_image_repository }}:latest

FROM ${BASE_IMAGE}

ADD tmpdir/root.tar /

# Configure start
ENV HOME=/root
WORKDIR /root
CMD bash -l
