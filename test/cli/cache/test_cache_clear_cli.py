#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.cache.CacheClearCli."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.cli.cache.cache_clear_cli import CacheClearCli
from scinoephile.cli.cache.cache_cli import CacheCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (CacheClearCli,),
        (CacheCli, CacheClearCli),
        (ScinoephileCli, CacheCli, CacheClearCli),
    ],
)
def test_cache_clear_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test cache clear CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (CacheClearCli,),
        (CacheCli, CacheClearCli),
        (ScinoephileCli, CacheCli, CacheClearCli),
    ],
)
def test_cache_clear_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test cache clear CLI usage when called with no arguments.

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
    (tmp_path / "llm" / "abc.json").write_text('{"result": 1}')
    (tmp_path / "transcription").mkdir()
    (tmp_path / "transcription" / "xyz.json").write_text('{"segments": []}')
    return tmp_path


def test_cache_clear_dry_run_namespace(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test that dry-run clear with a namespace reports files without deleting.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(
        CacheClearCli,
        f"--cache-dir {cache_dir} --namespace llm --dry-run",
    )
    out = capsys.readouterr().out
    assert "[dry-run]" in out
    assert "llm/abc.json" in out
    assert (cache_dir / "llm" / "abc.json").exists()


def test_cache_clear_confirmed_namespace(
    cache_dir: Path, capsys: pytest.CaptureFixture
):
    """Test that confirmed clear deletes all entries in the namespace.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(
        CacheClearCli,
        f"--cache-dir {cache_dir} --namespace llm --yes",
    )
    assert not (cache_dir / "llm" / "abc.json").exists()
    assert (cache_dir / "transcription" / "xyz.json").exists()


def test_cache_clear_all_dry_run(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test dry-run clear with --all reports all namespaces.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(
        CacheClearCli,
        f"--cache-dir {cache_dir} --all --dry-run",
    )
    out = capsys.readouterr().out
    assert "llm" in out
    assert "transcription" in out
    assert (cache_dir / "llm" / "abc.json").exists()
    assert (cache_dir / "transcription" / "xyz.json").exists()


def test_cache_clear_all_confirmed(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test confirmed clear with --all deletes entries from every namespace.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(
        CacheClearCli,
        f"--cache-dir {cache_dir} --all --yes",
    )
    assert not (cache_dir / "llm" / "abc.json").exists()
    assert not (cache_dir / "transcription" / "xyz.json").exists()


def test_cache_clear_refuses_without_yes(
    cache_dir: Path, capsys: pytest.CaptureFixture
):
    """Test that clear refuses to delete without --yes or --dry-run.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    with pytest.raises(SystemExit) as exc_info:
        run_cli_with_args(
            CacheClearCli,
            f"--cache-dir {cache_dir} --namespace llm",
        )
    assert exc_info.value.code == 2


def test_cache_clear_missing_namespace_or_all(
    cache_dir: Path, capsys: pytest.CaptureFixture
):
    """Test that clear without --namespace or --all causes a usage error.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    with pytest.raises(SystemExit) as exc_info:
        run_cli_with_args(
            CacheClearCli,
            f"--cache-dir {cache_dir} --yes",
        )
    assert exc_info.value.code == 2


def test_cache_clear_invalid_namespace(cache_dir: Path, capsys: pytest.CaptureFixture):
    """Test that clearing a non-existent namespace prints an error.

    Arguments:
        cache_dir: populated cache directory
        capsys: pytest stdout/stderr capture fixture
    """
    run_cli_with_args(
        CacheClearCli,
        f"--cache-dir {cache_dir} --namespace bogus --dry-run",
    )
    out = capsys.readouterr().out
    assert "Error:" in out


def test_cache_clear_missing_dir(tmp_path: Path, capsys: pytest.CaptureFixture):
    """Test clearing a missing cache dir prints 'No entries to clear.'

    Arguments:
        tmp_path: pytest temporary directory
        capsys: pytest stdout/stderr capture fixture
    """
    missing = tmp_path / "nonexistent"
    run_cli_with_args(
        CacheClearCli,
        f"--cache-dir {missing} --all --dry-run",
    )
    out = capsys.readouterr().out
    assert "No entries to clear." in out
