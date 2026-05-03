#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.cache.CacheStatsCli."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scinoephile.cli.cache.cache_cli import CacheCli
from scinoephile.cli.cache.cache_stats_cli import CacheStatsCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (CacheStatsCli,),
        (CacheCli, CacheStatsCli),
        (ScinoephileCli, CacheCli, CacheStatsCli),
    ],
)
def test_cache_stats_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test cache stats CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (CacheStatsCli,),
        (CacheCli, CacheStatsCli),
        (ScinoephileCli, CacheCli, CacheStatsCli),
    ],
)
def test_cache_stats_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test cache stats CLI usage when called with no arguments.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


@pytest.fixture
def cache_dir(tmp_path: Path) -> Path:
    """Create a temporary cache directory with test entries.

    Arguments:
        tmp_path: pytest temporary directory
    Returns:
        populated cache directory path
    """
    (tmp_path / "llm").mkdir()
    (tmp_path / "llm" / "abc123.json").write_text('{"result": 1}')
    (tmp_path / "transcription").mkdir()
    (tmp_path / "transcription" / "xyz.json").write_text('{"segments": []}')
    return tmp_path


def test_cache_stats_text(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test text-format stats output.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(CacheStatsCli, f"--cache-dir {cache_dir}")
    out = capsys.readouterr().out
    assert "llm" in out
    assert "transcription" in out
    assert "total:" in out


def test_cache_stats_json(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test JSON-format stats output.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(CacheStatsCli, f"--cache-dir {cache_dir} --format json")
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "namespaces" in data
    assert "total" in data
    assert data["total"]["count"] == 2


def test_cache_stats_namespace_filter(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test namespace filtering on stats output.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(
        CacheStatsCli, f"--cache-dir {cache_dir} --namespace llm --format json"
    )
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["total"]["count"] == 1
    assert len(data["namespaces"]) == 1
    assert data["namespaces"][0]["namespace"] == "llm"


def test_cache_stats_missing_dir(tmp_path: Path, capsys: pytest.CaptureFixture):
    """Test stats on a missing cache dir prints 'No cache entries found.'

    Arguments:
        tmp_path: pytest temporary directory
        capsys: pytest stdout/stderr capture fixture
    """
    missing = tmp_path / "nonexistent"
    run_cli_with_args(CacheStatsCli, f"--cache-dir {missing}")
    out = capsys.readouterr().out
    assert "No cache entries found." in out
