#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of optimization CLI parent command."""

from __future__ import annotations

from pathlib import Path

from pytest import CaptureFixture

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.utility.optimization.optimization_cli import OptimizationCli
from scinoephile.cli.utility.optimization.optimization_prompts_cli import (
    OptimizationSyncPromptsCli,
)
from scinoephile.cli.utility.optimization.optimization_test_cases_cli import (
    OptimizationSyncTestCasesCli,
)
from scinoephile.cli.utility.utility_cli import UtilityCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.optimization.persistence.prompts import PromptSqliteStore
from test.helpers import assert_cli_help


def test_optimization_subcommand_help():
    """Test optimization subcommand help output."""
    for cli_class in (OptimizationSyncPromptsCli, OptimizationSyncTestCasesCli):
        assert_cli_help((ScinoephileCli, UtilityCli, OptimizationCli, cli_class))


def test_sync_prompts_cli_dry_run(
    tmp_path: Path,
    capsys: CaptureFixture[str],
):
    """The prompt synchronization CLI should report a read-only dry run.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest output capture fixture
    """
    database_path = tmp_path / "optimization.sqlite"

    run_cli_with_args(
        OptimizationSyncPromptsCli,
        f"--prompt review-eng --outfile {database_path} --dry-run",
    )

    output = capsys.readouterr().out
    assert "insert-alias" in output
    assert not database_path.exists()


def test_sync_prompts_cli_writes_selected_alias(
    tmp_path: Path,
    capsys: CaptureFixture[str],
):
    """The prompt synchronization CLI should persist an explicit alias.

    Arguments:
        tmp_path: temporary directory
        capsys: pytest output capture fixture
    """
    database_path = tmp_path / "optimization.sqlite"

    run_cli_with_args(
        OptimizationSyncPromptsCli,
        f"--prompt review-eng --outfile {database_path}",
    )

    assert "'prompts': 1" in capsys.readouterr().out
    assert PromptSqliteStore(database_path).get_prompt_by_alias("review-eng")
