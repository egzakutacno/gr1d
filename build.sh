#!/bin/bash

# Create Dockerfile
cat > Dockerfile <<EOF
FROM eniocarboni/docker-ubuntu-systemd:jammy

RUN apt-get update && \
    apt-get install -y docker.io jq nano && \
    apt-get clean
EOF

# Build the docker image
docker build -t my-ubuntu-systemd-with-docker .
