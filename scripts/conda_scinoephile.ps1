#!/usr/bin/env pwsh
# Script for creating a working conda environment on Windows,
# with the latest version of required packages

$ErrorActionPreference="Stop"

conda deactivate
conda remove -y --name scinoephile --all
conda create -y --name scinoephile python=3.11
conda activate scinoephile

pip install `
    black `
    isort `
    mypy `
    prospector `
    pytest `
    pytest-cov `
    pytest-xdist
if (!$?)
{
    Exit $LASTEXITCODE
}
