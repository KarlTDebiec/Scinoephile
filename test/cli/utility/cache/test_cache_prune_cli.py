#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache prune CLI."""

from __future__ import annotations

from pathlib import Path
from time import time

from pytest import CaptureFixture, raises

from scinoephile.cli.utility.cache.cache_prune_cli import CachePruneCli
from scinoephile.common.testing import run_cli_with_args
from test.helpers.files import set_mtime, write_cache_file


def test_cache_prune_dry_run(tmp_path: Path, capsys: CaptureFixture[str]):
    """Test dry-run cache pruning.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    old_path = write_cache_file(tmp_path / "llm/old.json")
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
    old_path = write_cache_file(tmp_path / "llm/old.json")
    new_path = write_cache_file(tmp_path / "llm/new.json")
    _set_old(old_path)

    run_cli_with_args(CachePruneCli, f"--cache-dir {tmp_path} --older-than 30d --yes")

    assert not old_path.exists()
    assert new_path.exists()


def test_cache_prune_requires_confirmation(tmp_path: Path):
    """Test that prune requires confirmation.

    Arguments:
        tmp_path: temporary directory
    """
    with raises(SystemExit) as exc_info:
        run_cli_with_args(CachePruneCli, f"--cache-dir {tmp_path} --older-than 30d")
    assert exc_info.value.code == 2


def _set_old(path: Path):
    """Make a path older than thirty days.

    Arguments:
        path: path to modify
    """
    timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(path, timestamp)
