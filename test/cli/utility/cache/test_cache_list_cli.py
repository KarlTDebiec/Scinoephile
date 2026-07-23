#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache list CLI."""

from __future__ import annotations

import json
from pathlib import Path

from pytest import CaptureFixture

from scinoephile.cli.utility.cache.cache_list_cli import CacheListCli
from scinoephile.common.testing import run_cli_with_args
from test.helpers.files import write_cache_file


def test_cache_list_text(tmp_path: Path, capsys: CaptureFixture[str]):
    """Test text cache list output.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    write_cache_file(tmp_path / "llm/one.json")
    write_cache_file(tmp_path / "whisper/two.json")

    run_cli_with_args(CacheListCli, f"--cache-dir {tmp_path} --namespace llm")

    assert "llm\tllm/one.json" in capsys.readouterr().out


def test_cache_list_json(tmp_path: Path, capsys: CaptureFixture[str]):
    """Test JSON cache list output.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    write_cache_file(tmp_path / "llm/one.json")

    run_cli_with_args(CacheListCli, f"--cache-dir {tmp_path} --format json")

    entries = json.loads(capsys.readouterr().out)
    assert entries[0]["namespace"] == "llm"
    assert entries[0]["path"] == "llm/one.json"


def test_cache_list_missing_root(tmp_path: Path, capsys: CaptureFixture[str]):
    """Test cache list output for a missing root.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    run_cli_with_args(CacheListCli, f"--cache-dir {tmp_path / 'missing'}")

    assert capsys.readouterr().out == "No cache entries found.\n"
