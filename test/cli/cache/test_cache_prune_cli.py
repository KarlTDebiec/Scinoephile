#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache prune CLI."""

from __future__ import annotations

from os import utime
from pathlib import Path
from time import time

import pytest

from scinoephile.cli.cache.cache_prune_cli import CachePruneCli
from scinoephile.common.testing import run_cli_with_args


def test_cache_prune_dry_run(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """Test dry-run cache pruning.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    old_path = _write_cache_file(tmp_path / "llm/old.json")
    _set_old(old_path)

    run_cli_with_args(
        CachePruneCli, f"--cache-dir {tmp_path} --older-than 30d --dry-run"
    )

    assert old_path.exists()
    assert "llm/old.json" in capsys.readouterr().out


def test_cache_prune_confirmed(tmp_path: Path):
    """Test confirmed cache pruning.

    Arguments:
        tmp_path: temporary directory
    """
    old_path = _write_cache_file(tmp_path / "llm/old.json")
    new_path = _write_cache_file(tmp_path / "llm/new.json")
    _set_old(old_path)

    run_cli_with_args(CachePruneCli, f"--cache-dir {tmp_path} --older-than 30d --yes")

    assert not old_path.exists()
    assert new_path.exists()


def test_cache_prune_requires_confirmation(tmp_path: Path):
    """Test that prune requires confirmation.

    Arguments:
        tmp_path: temporary directory
    """
    with pytest.raises(SystemExit) as exc_info:
        run_cli_with_args(CachePruneCli, f"--cache-dir {tmp_path} --older-than 30d")
    assert exc_info.value.code == 2


def _set_old(path: Path):
    """Make a path older than thirty days.

    Arguments:
        path: path to modify
    """
    timestamp = time() - 60 * 60 * 24 * 40
    utime(path, (timestamp, timestamp))


def _write_cache_file(path: Path) -> Path:
    """Write a cache file.

    Arguments:
        path: path to write
    Returns:
        written path
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}", encoding="utf-8")
    return path
