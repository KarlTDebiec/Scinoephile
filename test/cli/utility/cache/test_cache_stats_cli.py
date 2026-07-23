#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache stats CLI."""

from __future__ import annotations

import json
from pathlib import Path

from pytest import CaptureFixture

from scinoephile.cli.utility.cache.cache_stats_cli import CacheStatsCli
from scinoephile.common.testing import run_cli_with_args
from test.helpers.files import write_cache_file


def test_cache_stats_json(tmp_path: Path, capsys: CaptureFixture[str]):
    """Test JSON cache stats output.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    write_cache_file(tmp_path / "llm/one.json", "one")

    run_cli_with_args(CacheStatsCli, f"--cache-dir {tmp_path} --format json")

    stats = {item["namespace"]: item for item in json.loads(capsys.readouterr().out)}
    assert stats["llm"]["entry_count"] == 1
    assert stats["llm"]["total_bytes"] == 3
    assert stats["total"]["entry_count"] == 1


def test_cache_stats_namespace(tmp_path: Path, capsys: CaptureFixture[str]):
    """Test namespace-filtered cache stats output.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    write_cache_file(tmp_path / "llm/one.json")
    write_cache_file(tmp_path / "whisper/two.json")

    run_cli_with_args(CacheStatsCli, f"--cache-dir {tmp_path} --namespace whisper")

    output = capsys.readouterr().out
    assert "whisper\t1 entries" in output
    assert "llm\t" not in output
