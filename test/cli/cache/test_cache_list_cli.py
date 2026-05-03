#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.cache.CacheListCli."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scinoephile.cli.cache.cache_cli import CacheCli
from scinoephile.cli.cache.cache_list_cli import CacheListCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (CacheListCli,),
        (CacheCli, CacheListCli),
        (ScinoephileCli, CacheCli, CacheListCli),
    ],
)
def test_cache_list_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test cache list CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (CacheListCli,),
        (CacheCli, CacheListCli),
        (ScinoephileCli, CacheCli, CacheListCli),
    ],
)
def test_cache_list_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test cache list CLI usage output when called with no arguments.

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


def test_cache_list_text(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test text-format listing of cache entries.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(CacheListCli, f"--cache-dir {cache_dir}")
    out = capsys.readouterr().out
    assert "llm/abc123.json" in out
    assert "transcription/xyz.json" in out


def test_cache_list_json(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test JSON-format listing of cache entries.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(CacheListCli, f"--cache-dir {cache_dir} --format json")
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)
    assert len(data) == 2
    rel_paths = [row["rel_path"] for row in data]
    assert "abc123.json" in rel_paths
    assert "xyz.json" in rel_paths


def test_cache_list_jsonl(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test JSONL-format listing of cache entries.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(CacheListCli, f"--cache-dir {cache_dir} --format jsonl")
    out = capsys.readouterr().out
    rows = [json.loads(line) for line in out.strip().splitlines()]
    assert len(rows) == 2


def test_cache_list_namespace_filter(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test namespace filtering on list output.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(CacheListCli, f"--cache-dir {cache_dir} --namespace llm")
    out = capsys.readouterr().out
    assert "llm/abc123.json" in out
    assert "transcription" not in out


def test_cache_list_invalid_namespace(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test that listing with an invalid namespace prints an error.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(CacheListCli, f"--cache-dir {cache_dir} --namespace bogus")
    out = capsys.readouterr().out
    assert "Error:" in out


def test_cache_list_missing_dir(tmp_path: Path, capsys: pytest.CaptureFixture):
    """Test listing from a missing cache dir prints 'No cache entries found.'

    Arguments:
        tmp_path: pytest temporary directory
        capsys: pytest stdout/stderr capture fixture
    """
    missing = tmp_path / "nonexistent"
    run_cli_with_args(CacheListCli, f"--cache-dir {missing}")
    out = capsys.readouterr().out
    assert "No cache entries found." in out


def test_cache_list_limit(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test that --limit constrains the number of entries in the output.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(CacheListCli, f"--cache-dir {cache_dir} --format json --limit 1")
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 1
