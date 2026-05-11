#!/usr/bin/env bash
set -x
set -e
set -o pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "$script_dir/.." && pwd)"

pushd "$project_root"
trap popd EXIT

if [ -d .venv ]; then
    rm -vrf .venv
fi

python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install uv
uv sync --all-extras
