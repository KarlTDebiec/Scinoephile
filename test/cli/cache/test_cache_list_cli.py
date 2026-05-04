#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache list CLI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scinoephile.cli.cache.cache_list_cli import CacheListCli
from scinoephile.common.testing import run_cli_with_args


def test_cache_list_text(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """Test text cache list output.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    _write_cache_file(tmp_path / "llm" / "one.json")
    _write_cache_file(tmp_path / "whisper" / "two.json")

    run_cli_with_args(CacheListCli, f"--cache-dir {tmp_path} --namespace llm")

    assert "llm\tllm/one.json" in capsys.readouterr().out


def test_cache_list_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """Test JSON cache list output.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    _write_cache_file(tmp_path / "llm" / "one.json")

    run_cli_with_args(CacheListCli, f"--cache-dir {tmp_path} --format json")

    entries = json.loads(capsys.readouterr().out)
    assert entries[0]["namespace"] == "llm"
    assert entries[0]["path"] == "llm/one.json"


def test_cache_list_missing_root(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """Test cache list output for a missing root.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    run_cli_with_args(CacheListCli, f"--cache-dir {tmp_path / 'missing'}")

    assert capsys.readouterr().out == "No cache entries found.\n"


def _write_cache_file(path: Path):
    """Write a cache file.

    Arguments:
        path: path to write
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}", encoding="utf-8")
