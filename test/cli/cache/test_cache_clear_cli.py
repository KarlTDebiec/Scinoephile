#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache clear CLI."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.cli.cache.cache_clear_cli import CacheClearCli
from scinoephile.common.testing import run_cli_with_args


def test_cache_clear_dry_run(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """Test dry-run namespace clearing.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest capture fixture
    """
    cache_path = _write_cache_file(tmp_path / "llm" / "one.json")

    run_cli_with_args(
        CacheClearCli, f"--cache-dir {tmp_path} --namespace llm --dry-run"
    )

    assert cache_path.exists()
    assert "llm/one.json" in capsys.readouterr().out


def test_cache_clear_namespace_confirmed(tmp_path: Path):
    """Test confirmed namespace clearing.

    Arguments:
        tmp_path: temporary directory
    """
    _write_cache_file(tmp_path / "llm" / "one.json")
    whisper_path = _write_cache_file(tmp_path / "whisper" / "two.json")

    run_cli_with_args(CacheClearCli, f"--cache-dir {tmp_path} --namespace llm --yes")

    assert not (tmp_path / "llm").exists()
    assert whisper_path.exists()


def test_cache_clear_all_confirmed(tmp_path: Path):
    """Test confirmed clearing of all namespaces.

    Arguments:
        tmp_path: temporary directory
    """
    _write_cache_file(tmp_path / "llm" / "one.json")
    _write_cache_file(tmp_path / "whisper" / "two.json")

    run_cli_with_args(CacheClearCli, f"--cache-dir {tmp_path} --all --yes")

    assert not (tmp_path / "llm").exists()
    assert not (tmp_path / "whisper").exists()


def test_cache_clear_requires_scope(tmp_path: Path):
    """Test that clear requires an explicit scope.

    Arguments:
        tmp_path: temporary directory
    """
    with pytest.raises(SystemExit) as exc_info:
        run_cli_with_args(CacheClearCli, f"--cache-dir {tmp_path} --dry-run")
    assert exc_info.value.code == 2


def test_cache_clear_requires_confirmation(tmp_path: Path):
    """Test that clear requires confirmation.

    Arguments:
        tmp_path: temporary directory
    """
    with pytest.raises(SystemExit) as exc_info:
        run_cli_with_args(CacheClearCli, f"--cache-dir {tmp_path} --namespace llm")
    assert exc_info.value.code == 2


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
