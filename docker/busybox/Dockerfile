FROM busybox:1.29

# Fix bash
COPY files/ash2bash /bin/bash
RUN ln -s .bashrc /root/.profile
