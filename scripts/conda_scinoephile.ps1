#!/usr/bin/env pwsh
# Script for creating a working conda environment on Windows,
# with the latest version of required packages

$ErrorActionPreference="Stop"

conda deactivate
conda remove -y --name scinoephile --all
conda create -y --name scinoephile python=3.13

conda activate scinoephile

pip install uv

uv pip install `
    audioop-lts `
    ffmpeg-python `
    hanziconv `
    numba `
    numpy `
    openai `
    pillow `
    pycantonese `
    pydub `
    pypinyin `
    pyright `
    pysubs2 `
    pytest `
    pytest-cov `
    pytest-xdist `
    ruff `
    snownlp `
    svglib `
    transformers

uv pip install `
    torch `
    torchvision `
    torchaudio `
    --index-url https://download.pytorch.org/whl/cu128

