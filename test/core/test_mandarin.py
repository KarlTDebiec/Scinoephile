#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for Mandarin Chinese processing."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.mandarin import (
    get_mandarin_romanization,
    get_mandarin_text_romanization,
)
from ..data.kob import kob_cmn_hans_hk
from ..data.t import t_input_hanzi


def _test_get_mandarin_romanization(series: Series):
    output = get_mandarin_romanization(series)
    assert len(series.events) == len(output.events)


def test_get_mandarin_romanization_kob(kob_cmn_hans_hk: Series):
    _test_get_mandarin_romanization(kob_cmn_hans_hk)


def test_get_mandarin_romanization_t(t_input_hanzi: Series):
    _test_get_mandarin_romanization(t_input_hanzi)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("你好世界", "nǐ hǎo shìjiè"),
    ],
)
def test_get_mandarin_text_romanization(text: str, expected: str):
    assert get_mandarin_text_romanization(text) == expected
