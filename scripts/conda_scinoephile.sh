#!/usr/bin/env bash
# Script for creating a working conda environment on Unix-like systems,
# with the latest version of required packages

set -euo pipefail

conda deactivate || true
conda remove -y --name scinoephile --all || true
conda create -y --name scinoephile python=3.13
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate scinoephile

pip install uv

uv pip install \
    audioop-lts \
    ffmpeg-python \
    hanziconv \
    numba \
    numpy \
    openai \
    pillow \
    pycantonese \
    pydub \
    pypinyin \
    pyright \
    pysubs2 \
    pytest \
    pytest-cov \
    pytest-xdist \
    ruff \
    snownlp \
    svglib \
    transformers

conda install -y -c pytorch \
    pytorch \
    torchaudio
