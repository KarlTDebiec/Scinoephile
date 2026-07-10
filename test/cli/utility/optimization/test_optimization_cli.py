#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of optimization CLI parent command."""

from __future__ import annotations

from argparse import ArgumentTypeError

from pytest import raises

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.utility.optimization.argument_types import source_prompt_arg
from scinoephile.cli.utility.optimization.optimization_cli import OptimizationCli
from scinoephile.cli.utility.optimization.optimization_test_cases_cli import (
    OptimizationSyncTestCasesCli,
)
from scinoephile.cli.utility.utility_cli import UtilityCli
from scinoephile.lang.zho.review import ReviewPromptZhoHant
from test.helpers import assert_cli_help


def test_optimization_subcommand_help():
    """Test optimization subcommand help output."""
    assert_cli_help(
        (ScinoephileCli, UtilityCli, OptimizationCli, OptimizationSyncTestCasesCli)
    )


def test_source_prompt_arg_imports_prompt_class():
    """Source prompt arguments should import concrete prompt classes."""
    assert (
        source_prompt_arg("scinoephile.lang.zho.review.ReviewPromptZhoHant")
        is ReviewPromptZhoHant
    )


def test_source_prompt_arg_rejects_non_prompt_class():
    """Source prompt arguments should reject non-prompt classes."""
    with raises(ArgumentTypeError, match="is not a prompt class"):
        source_prompt_arg("pathlib.Path")
