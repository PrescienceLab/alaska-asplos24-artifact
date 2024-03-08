from ubuntu:22.04 as build
MAINTAINER Nick Wanninger <ncw@u.northwestern.edu>

RUN apt-get update && apt-get install -y \
  build-essential \
  git \
  python3 python3-pip python3-virtualenv \
  python2 \
  sudo \
  libxml2 \
  cmake \
  wget \
  libunwind-dev \
  file \
  default-jre

WORKDIR /artifact

COPY . .

ENTRYPOINT ["/usr/bin/bash"]
