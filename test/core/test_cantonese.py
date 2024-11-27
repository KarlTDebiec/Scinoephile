#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for Cantonese subtitle processing."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
# noinspection PyProtectedMember
from scinoephile.core.cantonese import (
    _get_cantonese_text_romanization,
    get_cantonese_romanization,
)
from ..data.kob import kob_cmn_hans_hk


def _test_get_cantonese_romanization(series: Series):
    output = get_cantonese_romanization(series)
    assert len(series.events) == len(output.events)


def test_get_cantonese_romanization_kob(kob_cmn_hans_hk: Series):
    _test_get_cantonese_romanization(kob_cmn_hans_hk)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("你好世界", "néih hóu sai gaai"),
    ],
)
def test_get_cantonese_text_romanization(text: str, expected: str):
    assert _get_cantonese_text_romanization(text) == expected
