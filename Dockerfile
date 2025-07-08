FROM debian:trixie

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3.13 \
    python3.13-venv \
    python3.13-dev \
    # other packages...
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.13 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1 && \
    python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN python -m pip install --upgrade pip
RUN pip install uv

WORKDIR /app
