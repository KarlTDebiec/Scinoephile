#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache inspect CLI."""

from __future__ import annotations

import json
from pathlib import Path
from time import time

from pytest import CaptureFixture

from scinoephile.cli.utility.cache.cache_inspect_cli import CacheInspectCli
from scinoephile.common.testing import run_cli_with_args
from test.helpers.files import set_mtime, write_cache_file


def test_cache_inspect_summary_json(tmp_path: Path, capsys: CaptureFixture[str]):
    """Test JSON cache summary output.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    write_cache_file(tmp_path / "llms/test/one.json", "one")

    run_cli_with_args(CacheInspectCli, f"--cache-dir {tmp_path} --format json")

    stats = {item["namespace"]: item for item in json.loads(capsys.readouterr().out)}
    assert stats["llms/test"]["entry_count"] == 1
    assert stats["llms/test"]["total_bytes"] == 3
    assert stats["total"]["entry_count"] == 1
    assert "oldest_accessed_at" not in stats["total"]


def test_cache_inspect_summary_namespace(tmp_path: Path, capsys: CaptureFixture[str]):
    """Test namespace-filtered cache summary output.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    write_cache_file(tmp_path / "llms/test/one.json")
    write_cache_file(tmp_path / "audio/transcription/whisper/two.json")

    run_cli_with_args(
        CacheInspectCli,
        f"--cache-dir {tmp_path} --namespace audio/transcription/whisper",
    )

    output = capsys.readouterr().out
    assert "audio/transcription/whisper\t1 entries" in output
    assert "llms/test\t" not in output


def test_cache_inspect_summary_by_age(tmp_path: Path, capsys: CaptureFixture[str]):
    """Test age-filtered cache summary output.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    old_path = write_cache_file(tmp_path / "llms/test/old.json")
    write_cache_file(tmp_path / "llms/test/new.json")
    timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(old_path, timestamp)

    run_cli_with_args(
        CacheInspectCli, f"--cache-dir {tmp_path} --older-than 30d --format json"
    )

    stats = {item["namespace"]: item for item in json.loads(capsys.readouterr().out)}
    assert stats["llms/test"]["entry_count"] == 1
    assert stats["total"]["entry_count"] == 1


def test_cache_inspect_entries(tmp_path: Path, capsys: CaptureFixture[str]):
    """Test detailed cache entry output.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    write_cache_file(tmp_path / "llms/test/one.json")
    write_cache_file(tmp_path / "audio/transcription/whisper/two.json")

    run_cli_with_args(
        CacheInspectCli, f"--cache-dir {tmp_path} --namespace llms/test --entries"
    )

    output = capsys.readouterr().out
    assert "llms/test\tllms/test/one.json" in output
    assert "atime" not in output


def test_cache_inspect_entries_by_age_json(tmp_path: Path, capsys: CaptureFixture[str]):
    """Test age-filtered detailed JSON output.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    old_path = write_cache_file(tmp_path / "llms/test/old.json")
    write_cache_file(tmp_path / "llms/test/new.json")
    timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(old_path, timestamp)

    run_cli_with_args(
        CacheInspectCli,
        f"--cache-dir {tmp_path} --entries --older-than 30d --format json",
    )

    entries = json.loads(capsys.readouterr().out)
    assert [entry["path"] for entry in entries] == ["llms/test/old.json"]
    assert "accessed_at" not in entries[0]


def test_cache_inspect_entries_missing_root(
    tmp_path: Path, capsys: CaptureFixture[str]
):
    """Test detailed output for a missing cache root.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    run_cli_with_args(CacheInspectCli, f"--cache-dir {tmp_path / 'missing'} --entries")

    assert capsys.readouterr().out == "No cache entries found.\n"
