#!/usr/bin/env bash
set -x
set -e  # Exit on error
set -o pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "$script_dir/.." && pwd)"

pushd "$project_root" > /dev/null
trap 'popd > /dev/null' EXIT

# Remove existing virtual environment
if [ -d .venv ]; then
    rm -vrf .venv
fi

# Set up virtual environment with uv
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install uv

# Install requirements
uv sync --all-extras
