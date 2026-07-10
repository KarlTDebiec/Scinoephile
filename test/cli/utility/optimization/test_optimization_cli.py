#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of optimization CLI parent command."""

from __future__ import annotations

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.utility.optimization.optimization_cli import OptimizationCli
from scinoephile.cli.utility.optimization.optimization_test_cases_cli import (
    OptimizationSyncTestCasesCli,
)
from scinoephile.cli.utility.utility_cli import UtilityCli
from test.helpers import assert_cli_help


def test_optimization_subcommand_help():
    """Test optimization subcommand help output."""
    assert_cli_help(
        (ScinoephileCli, UtilityCli, OptimizationCli, OptimizationSyncTestCasesCli)
    )
