#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of optimization list-operations CLI."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest

from scinoephile.cli.optimization.optimization_cli import OptimizationCli
from scinoephile.cli.optimization.optimization_list_operations_cli import (
    OptimizationListOperationsCli,
)
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args
from test.helpers import assert_cli_help


@pytest.mark.parametrize(
    "cli",
    [
        (OptimizationListOperationsCli,),
        (OptimizationCli, OptimizationListOperationsCli),
        (ScinoephileCli, OptimizationCli, OptimizationListOperationsCli),
    ],
)
def test_optimization_list_operations_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test optimization list-operations CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (OptimizationListOperationsCli,),
        (OptimizationCli, OptimizationListOperationsCli),
        (ScinoephileCli, OptimizationCli, OptimizationListOperationsCli),
    ],
)
def test_optimization_list_operations(cli: tuple[type[CommandLineInterface], ...]):
    """Test optimization list-operations CLI lists operations.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    subcommands = " ".join(command.name() for command in cli[1:])
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout):
        with redirect_stderr(stderr):
            run_cli_with_args(cli[0], subcommands)
    assert "Available operations:" in stdout.getvalue()
    assert "eng-block-review" in stdout.getvalue()
    assert stderr.getvalue() == ""
