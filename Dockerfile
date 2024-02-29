from ubuntu:22.04 as build
MAINTAINER Nick Wanninger <ncw@u.northwestern.edu>

RUN apt-get update && apt-get install -y \
  build-essential \
  git \
  python3 python3-pip python3-virtualenv \
  sudo \
  libxml2 \
  cmake \
  wget \
  libunwind-dev \
  file \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*


WORKDIR /src

COPY . .

# Make sure the virtual environment is created
RUN make venv

# Compile alaska into /src/opt
RUN make compile

# Create figure 7
RUN make results/figure7.pdf

FROM scratch as output
COPY --from=build /src/results .
