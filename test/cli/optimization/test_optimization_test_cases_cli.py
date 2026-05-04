#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.optimization.OptimizationSyncTestCasesCli."""

from __future__ import annotations

import ast
import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from scinoephile.cli.optimization.optimization_cli import OptimizationCli
from scinoephile.cli.optimization.optimization_test_cases_cli import (
    OptimizationSyncTestCasesCli,
)
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args
from scinoephile.optimization.operations import OPERATIONS
from scinoephile.optimization.persistence.test_cases import TestCaseSqliteStore
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (OptimizationSyncTestCasesCli,),
        (OptimizationCli, OptimizationSyncTestCasesCli),
        (ScinoephileCli, OptimizationCli, OptimizationSyncTestCasesCli),
    ],
)
def test_optimization_sync_test_cases_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test optimization sync-test-cases CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (OptimizationSyncTestCasesCli,),
        (OptimizationCli, OptimizationSyncTestCasesCli),
        (ScinoephileCli, OptimizationCli, OptimizationSyncTestCasesCli),
    ],
)
def test_optimization_sync_test_cases_usage(
    cli: tuple[type[CommandLineInterface], ...],
):
    """Test optimization sync-test-cases CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_optimization_sync_test_cases_cli_dry_run_and_apply(tmp_path: Path):
    """Test optimization sync-test-cases dry-run and apply modes.

    Arguments:
        tmp_path: temporary directory for input and output files
    """
    operation = "eng-block-review"
    spec = OPERATIONS[operation]

    infile_path = tmp_path / "test_cases.json"
    db_path = tmp_path / "test_cases.sqlite"

    data = [
        {
            "query": {"subtitle_1": "Hello."},
            "answer": {"revised_1": "", "note_1": ""},
            "verified": True,
        }
    ]
    infile_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout):
        with redirect_stderr(stderr):
            run_cli_with_args(
                OptimizationSyncTestCasesCli,
                f"--infile {infile_path} --operation {operation} "
                f"--outfile {db_path} --dry-run",
            )
    assert stderr.getvalue() == ""

    lines = [ln for ln in stdout.getvalue().splitlines() if ln.strip()]
    assert len(lines) >= 1
    row = ast.literal_eval(lines[0])
    assert row["action"] == "insert"
    assert len(row["test_case_id"]) == 64
    assert not db_path.exists()

    # Apply the sync; should insert the row and link to the source path.
    run_cli_with_args(
        OptimizationSyncTestCasesCli,
        f"--infile {infile_path} --operation {operation} --outfile {db_path}",
    )
    store = TestCaseSqliteStore(db_path)
    loaded = store.get_test_case(spec.test_case_table_name, row["test_case_id"])
    assert loaded is not None
    assert loaded.query == {"subtitle_1": "Hello."}
    assert loaded.answer == {"revised_1": "", "note_1": ""}
