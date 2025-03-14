#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.mandarin."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.mandarin import (
    _get_mandarin_text_romanization,
    get_mandarin_romanization,
)
from ..data.mnt import mnt_zho_hant
from ..data.pdp import pdp_zho_hant
from ..data.t import t_zho_hans


def _test_get_mandarin_romanization(series: Series):
    output = get_mandarin_romanization(series)
    assert len(series.events) == len(output.events)


# get_mandarin_romanization
def test_get_mandarin_romanization_mnt(mnt_zho_hant: Series):
    _test_get_mandarin_romanization(mnt_zho_hant)


def test_get_mandarin_romanization_pdp(pdp_zho_hant: Series):
    _test_get_mandarin_romanization(pdp_zho_hant)


def test_get_mandarin_romanization_t(t_zho_hans: Series):
    _test_get_mandarin_romanization(t_zho_hans)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("你好世界", "nǐ hǎo shìjiè"),
    ],
)
def test_get_mandarin_text_romanization(text: str, expected: str):
    assert _get_mandarin_text_romanization(text) == expected
