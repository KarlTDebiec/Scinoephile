#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.DictionaryCli."""

from __future__ import annotations

import pytest

from scinoephile.cli import (
    DictionaryCli,
    ScinoephileCli,
)
from scinoephile.common import CommandLineInterface
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (DictionaryCli,),
        (ScinoephileCli, DictionaryCli),
    ],
)
def test_dictionary_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test dictionary CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (DictionaryCli,),
        (ScinoephileCli, DictionaryCli),
    ],
)
def test_dictionary_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test dictionary CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)
