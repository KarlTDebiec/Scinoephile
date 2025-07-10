#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for Scinoephile command-line interface."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from inspect import getfile
from io import StringIO
from pathlib import Path

import pytest

from scinoephile.cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args


@pytest.mark.parametrize(
    "cli",
    [
        (ScinoephileCli,),
    ],
)
def test_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test CLI help.

    Arguments:
        cli: CLI class to test
    """
    subcommands = " ".join(f"{command.name()}" for command in cli[1:])

    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(cli[0], f"{subcommands} -h")
    except SystemExit as error:
        assert error.code == 0
        assert stdout.getvalue().startswith(
            f"usage: {Path(getfile(cli[0])).name} {subcommands}"
        )
        assert stderr.getvalue() == ""


@pytest.mark.parametrize(
    "cli",
    [
        (ScinoephileCli,),
    ],
)
def test_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test CLI usage.

    Arguments:
        cli: CLI class to test
    """
    subcommands = " ".join(f"{command.name()}" for command in cli[1:])

    stdout = StringIO()
    stderr = StringIO()
    try:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(cli[0], subcommands)
    except SystemExit as error:
        assert error.code == 2
        assert stdout.getvalue() == ""
        assert stderr.getvalue().startswith(
            f"usage: {Path(getfile(cli[0])).name} {subcommands}"
        )
