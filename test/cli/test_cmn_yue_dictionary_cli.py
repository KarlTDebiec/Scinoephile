#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.CmnYueDictionaryCli."""

from __future__ import annotations

import pytest

from scinoephile.cli import CmnYueDictionaryCli, ScinoephileCli
from scinoephile.common import CommandLineInterface
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (CmnYueDictionaryCli,),
        (ScinoephileCli, CmnYueDictionaryCli),
    ],
)
def test_cmn_yue_dictionary_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test CUHK dictionary CLI help output."""
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (CmnYueDictionaryCli,),
        (ScinoephileCli, CmnYueDictionaryCli),
    ],
)
def test_cmn_yue_dictionary_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test CUHK dictionary CLI usage output."""
    assert_cli_usage(cli)
