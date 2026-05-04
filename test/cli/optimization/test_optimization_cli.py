#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of optimization CLI parent command."""

from __future__ import annotations

import pytest

from scinoephile.cli.optimization.optimization_cli import OptimizationCli
from scinoephile.cli.optimization.optimization_test_cases_cli import (
    OptimizationSyncTestCasesCli,
)
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (OptimizationCli,),
        (ScinoephileCli, OptimizationCli),
    ],
)
def test_optimization_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test optimization CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (OptimizationCli,),
        (ScinoephileCli, OptimizationCli),
    ],
)
def test_optimization_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test optimization CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_optimization_subcommand_help():
    """Test optimization subcommand help output."""
    assert_cli_help((OptimizationCli, OptimizationSyncTestCasesCli))
