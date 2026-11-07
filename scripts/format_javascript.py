#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Format tracked JavaScript using pyproject.toml, excluding vendored *.min.js.

Run with `uv run python scripts/format_javascript.py`; add `--check` to report
formatting differences without changing files.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

import jsbeautifier


def _main() -> int:
    """Format first-party scripts or check their formatting without writing.

    Returns:
        exit status, nonzero when check mode finds differences or tooling fails
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check without writing")
    args = parser.parse_args()
    root_dir_path = Path(__file__).resolve().parent.parent
    try:
        with (root_dir_path / "pyproject.toml").open("rb") as configuration:
            options = tomllib.load(configuration)["tool"]["jsbeautifier"]
        tracked = subprocess.check_output(
            ["git", "ls-files", "-z", "--", "*.js", ":(exclude)*.min.js"],
            cwd=root_dir_path,
        ).decode("utf-8")
        differences = 0
        for name in tracked.split("\0"):
            if not name:
                continue
            file_path = root_dir_path / name
            source = file_path.read_text(encoding="utf-8")
            formatted = jsbeautifier.beautify(source, options)
            if source == formatted:
                continue
            differences += 1
            if args.check:
                print(f"Would reformat: {name}")
            else:
                file_path.write_text(formatted, encoding="utf-8", newline="\n")
                print(f"Reformatted: {name}")
    except (
        OSError,
        UnicodeError,
        ValueError,
        KeyError,
        subprocess.CalledProcessError,
    ) as exc:
        parser.exit(2, f"JavaScript formatting failed: {exc}\n")
    if args.check and differences:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
