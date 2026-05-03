#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.cache.CachePruneCli."""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

from scinoephile.cli.cache.cache_cli import CacheCli
from scinoephile.cli.cache.cache_prune_cli import CachePruneCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (CachePruneCli,),
        (CacheCli, CachePruneCli),
        (ScinoephileCli, CacheCli, CachePruneCli),
    ],
)
def test_cache_prune_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test cache prune CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (CachePruneCli,),
        (CacheCli, CachePruneCli),
        (ScinoephileCli, CacheCli, CachePruneCli),
    ],
)
def test_cache_prune_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test cache prune CLI usage when called with no arguments.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


@pytest.fixture
def cache_dir(tmp_path: Path) -> Path:
    """Create a cache directory with one old and one recent entry.

    Arguments:
        tmp_path: pytest temporary directory
    Returns:
        populated cache directory path
    """
    llm_dir = tmp_path / "llm"
    llm_dir.mkdir()
    old_file = llm_dir / "old.json"
    old_file.write_text('{"result": 1}')
    new_file = llm_dir / "new.json"
    new_file.write_text('{"result": 2}')

    old_time = time.time() - 10 * 24 * 3600  # 10 days ago
    os.utime(old_file, (old_time, old_time))
    return tmp_path


def test_cache_prune_dry_run(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test that dry-run prune reports files without deleting them.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(
        CachePruneCli,
        f"--cache-dir {cache_dir} --older-than 7d --dry-run",
    )
    out = capsys.readouterr().out
    assert "[dry-run]" in out
    assert "old.json" in out
    assert (cache_dir / "llm" / "old.json").exists()


def test_cache_prune_confirmed(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test that confirmed prune deletes old files.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(
        CachePruneCli,
        f"--cache-dir {cache_dir} --older-than 7d --yes",
    )
    assert not (cache_dir / "llm" / "old.json").exists()
    assert (cache_dir / "llm" / "new.json").exists()


def test_cache_prune_refuses_without_yes(
    cache_dir: Path, capsys: pytest.CaptureFixture
):
    """Test that prune refuses to delete without --yes or --dry-run.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    with pytest.raises(SystemExit) as exc_info:
        run_cli_with_args(
            CachePruneCli,
            f"--cache-dir {cache_dir} --older-than 7d",
        )
    assert exc_info.value.code == 2


def test_cache_prune_invalid_duration(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test that an invalid duration string causes a usage error.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    with pytest.raises(SystemExit) as exc_info:
        run_cli_with_args(
            CachePruneCli,
            f"--cache-dir {cache_dir} --older-than invalid --yes",
        )
    assert exc_info.value.code == 2


def test_cache_prune_no_matches(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test prune when no entries are old enough to delete.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(
        CachePruneCli,
        f"--cache-dir {cache_dir} --older-than 1s --dry-run",
    )
    out = capsys.readouterr().out
    assert "No entries to prune." in out
