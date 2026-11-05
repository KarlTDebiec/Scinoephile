#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of source-file discovery for repository checks."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import AbstractContextManager
from os import DirEntry, scandir
from pathlib import Path

from pytest import MonkeyPatch

from test.helpers.files import get_python_files


def test_source_discovery_prunes_generated_directories(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Keep nested sources without traversing environments or generated output.

    Arguments:
        tmp_path: temporary repository root
        monkeypatch: fixture for recording directory traversal
    """
    for name in (
        "package/z.py",
        "package/nested/a.py",
        "package/readme.md",
        "package/__pycache__/generated.py",
        ".venv/lib/dependency.py",
        "local/scratch.py",
    ):
        file_path = tmp_path / name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

    # Record actual traversal so filtering results after scanning cannot pass
    visited = []

    def recording_scandir(
        dir_path: str,
    ) -> AbstractContextManager[Iterator[DirEntry[str]]]:
        """Record each directory opened by the walker.

        Arguments:
            dir_path: directory being opened
        Returns:
            directory entry iterator
        """
        visited.append(Path(dir_path).relative_to(tmp_path))
        return scandir(dir_path)

    monkeypatch.setattr("os.scandir", recording_scandir)

    assert get_python_files(tmp_path) == [
        tmp_path / "package/nested/a.py",
        tmp_path / "package/z.py",
    ]
    assert set(visited) == {Path("."), Path("package"), Path("package/nested")}
