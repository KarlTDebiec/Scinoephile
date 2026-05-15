#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of command-line argument conflict handling style."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common import package_root


def test_cli_argument_conflicts_do_not_raise_only_to_catch():
    """Test CLIs do not raise argument conflicts only to report them immediately."""
    cli_dir_path = package_root / "cli"
    matching_paths = [
        file_path.relative_to(package_root.parent)
        for file_path in sorted(cli_dir_path.rglob("*.py"))
        if _has_argument_conflict_raise_in_try_block(file_path)
    ]

    assert matching_paths == []


def _has_argument_conflict_raise_in_try_block(file_path: Path) -> bool:
    """Check whether a file raises an argument conflict inside a try block.

    Arguments:
        file_path: Python source file path
    Returns:
        whether a try block raises ArgumentConflictError directly
    """
    lines = file_path.read_text(encoding="utf-8").splitlines()
    for line_index, line in enumerate(lines):
        if line.strip() != "try:":
            continue
        indent = len(line) - len(line.lstrip())
        for child_line in lines[line_index + 1 :]:
            if not child_line.strip():
                continue
            child_indent = len(child_line) - len(child_line.lstrip())
            if child_indent <= indent:
                break
            if child_line.strip().startswith("raise ArgumentConflictError("):
                return True
    return False
