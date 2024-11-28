#!/usr/bin/env pwsh
# Script for creating a working conda environment on Windows,
# with the latest version of required packages

$ErrorActionPreference="Stop"

conda deactivate
conda remove -y --name scinoephile --all
conda create -y --name scinoephile python=3.13
conda activate scinoephile

pip install `
    black `
    h5py `
    hanziconv `
    isort `
    mypy `
    nltk `
    numba `
    numpy `
    openai `
    opencv-python `
    pandas `
    pandas-stubs `
    pillow `
    prospector `
    pycantonese `
    pypinyin `
    pyright `
    pysubs2 `
    pytest `
    pytest-cov `
    pytest-xdist `
    snownlp
if (!$?)
{
    Exit $LASTEXITCODE
}
