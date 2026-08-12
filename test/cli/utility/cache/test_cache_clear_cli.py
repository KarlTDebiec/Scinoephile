#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache clear CLI."""

from __future__ import annotations

from pathlib import Path
from time import time

from pytest import CaptureFixture, raises

from scinoephile.cli.utility.cache.cache_clear_cli import CacheClearCli
from scinoephile.common.testing import run_cli_with_args
from test.helpers.files import set_mtime, write_cache_file


def test_cache_clear_dry_run(tmp_path: Path, capsys: CaptureFixture[str]):
    """Test dry-run namespace clearing.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    cache_path = write_cache_file(tmp_path / "llm/test/one.json")

    run_cli_with_args(
        CacheClearCli, f"--cache-dir {tmp_path} --namespace llm/test --dry-run"
    )

    assert cache_path.exists()
    assert "llm/test/one.json" in capsys.readouterr().out


def test_cache_clear_all_dry_run_limits_output(
    tmp_path: Path, capsys: CaptureFixture[str]
):
    """Test all-namespace dry-run output is bounded.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    write_cache_file(tmp_path / "llm/test/one.json")
    write_cache_file(tmp_path / "llm/test/two.json")
    write_cache_file(tmp_path / "whisper/three.json")

    run_cli_with_args(
        CacheClearCli, f"--cache-dir {tmp_path} --all --dry-run --limit 2"
    )

    output = capsys.readouterr().out
    assert output.count("\n") == 3
    assert "Showing 2 of 3 entries." in output


def test_cache_clear_namespace_confirmed(tmp_path: Path):
    """Test confirmed namespace clearing.

    Arguments:
        tmp_path: temporary directory
    """
    write_cache_file(tmp_path / "llm/test/one.json")
    whisper_path = write_cache_file(tmp_path / "whisper/two.json")

    run_cli_with_args(
        CacheClearCli, f"--cache-dir {tmp_path} --namespace llm/test --yes"
    )

    assert not (tmp_path / "llm").exists()
    assert whisper_path.exists()


def test_cache_clear_all_confirmed(tmp_path: Path):
    """Test confirmed clearing of all namespaces.

    Arguments:
        tmp_path: temporary directory
    """
    write_cache_file(tmp_path / "llm/test/one.json")
    write_cache_file(tmp_path / "whisper/two.json")

    run_cli_with_args(CacheClearCli, f"--cache-dir {tmp_path} --all --yes")

    assert not (tmp_path / "llm").exists()
    assert not (tmp_path / "whisper").exists()


def test_cache_clear_older_than_dry_run(tmp_path: Path, capsys: CaptureFixture[str]):
    """Test dry-run age-filtered clearing.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    old_path = write_cache_file(tmp_path / "llm/test/old.json")
    new_path = write_cache_file(tmp_path / "llm/test/new.json")
    _set_old(old_path)

    run_cli_with_args(
        CacheClearCli, f"--cache-dir {tmp_path} --all --older-than 30d --dry-run"
    )

    output = capsys.readouterr().out
    assert "llm/test/old.json" in output
    assert "llm/test/new.json" not in output
    assert old_path.exists()
    assert new_path.exists()


def test_cache_clear_older_than_confirmed(tmp_path: Path):
    """Test confirmed age-filtered clearing.

    Arguments:
        tmp_path: temporary directory
    """
    old_path = write_cache_file(tmp_path / "llm/test/old.json")
    new_path = write_cache_file(tmp_path / "llm/test/new.json")
    _set_old(old_path)

    run_cli_with_args(
        CacheClearCli, f"--cache-dir {tmp_path} --all --older-than 30d --yes"
    )

    assert not old_path.exists()
    assert new_path.exists()


def test_cache_clear_requires_scope(tmp_path: Path):
    """Test that clear requires an explicit scope.

    Arguments:
        tmp_path: temporary directory
    """
    with raises(SystemExit) as exc_info:
        run_cli_with_args(CacheClearCli, f"--cache-dir {tmp_path} --dry-run")
    assert exc_info.value.code == 2


def test_cache_clear_requires_confirmation(tmp_path: Path):
    """Test that clear requires confirmation.

    Arguments:
        tmp_path: temporary directory
    """
    with raises(SystemExit) as exc_info:
        run_cli_with_args(CacheClearCli, f"--cache-dir {tmp_path} --namespace llm/test")
    assert exc_info.value.code == 2


def _set_old(path: Path):
    """Make a path older than thirty days.

    Arguments:
        path: path to modify
    """
    timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(path, timestamp)
