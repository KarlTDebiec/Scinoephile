#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.DictionaryBuildCli."""

from __future__ import annotations

import pytest

from scinoephile.cli import (
    DictionaryBuildCli,
    DictionaryCli,
    ScinoephileCli,
)
from scinoephile.common import CommandLineInterface
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (DictionaryBuildCli,),
        (DictionaryCli, DictionaryBuildCli),
        (ScinoephileCli, DictionaryCli, DictionaryBuildCli),
    ],
)
def test_dictionary_build_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test dictionary build CLI help output."""
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (DictionaryBuildCli,),
        (DictionaryCli, DictionaryBuildCli),
        (ScinoephileCli, DictionaryCli, DictionaryBuildCli),
    ],
)
def test_dictionary_build_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test dictionary build CLI usage output."""
    assert_cli_usage(cli)
