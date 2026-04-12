#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.CmnYueCli."""

from __future__ import annotations

import pytest

from scinoephile.cli import CmnYueCli
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (CmnYueCli,),
    ],
)
def test_cmn_yue_help(cli):
    """Test 中文/粤文 CLI help output."""
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (CmnYueCli,),
    ],
)
def test_cmn_yue_usage(cli):
    """Test 中文/粤文 CLI usage output."""
    assert_cli_usage(cli)
