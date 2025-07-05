#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

$scriptDir = $PSScriptRoot
$projectRoot = Join-Path $scriptDir ".." | Resolve-Path | Select-Object -ExpandProperty Path

Push-Location $projectRoot
try {
    # Remove existing virtual environment
    if (Test-Path .venv) {
        Remove-Item -Recurse -Force .venv
    }

    # Set up virtual environment with uv
    python -m venv .venv
    . .venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install uv

    # Install requirements
    uv sync --all-extras
}
finally {
    Pop-Location
}
