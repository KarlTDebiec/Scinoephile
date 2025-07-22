#!/usr/bin/env bash
set -e
set -o pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd "$script_dir/.." && pwd)"

hooks_src="$project_root/scripts/git_hooks"
hooks_dest="$project_root/.git/hooks"

for hook in "$hooks_src"/*; do
    hook_name="$(basename "$hook")"
    cp "$hook" "$hooks_dest/$hook_name"
    chmod +x "$hooks_dest/$hook_name"
    echo "Installed $hook_name" >&2
done
