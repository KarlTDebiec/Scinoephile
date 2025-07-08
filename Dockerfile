FROM python:3.13-bookworm

# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv
