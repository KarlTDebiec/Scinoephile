#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.hanzi."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.hanzi import (
    _get_hanzi_text_flattened,  # noqa
    _get_hanzi_text_simplified,  # noqa
    get_hanzi_flattened,
    get_hanzi_simplified,
)
from ..data.kob import (
    kob_yue_hans_hk,
    kob_yue_hans_hk_flatten,
    kob_yue_hant_hk,
    kob_yue_hant_hk_simplify,
)
from ..data.mnt import (
    mnt_cmn_hant_hk,
    mnt_cmn_hant_hk_flatten,
    mnt_cmn_hant_hk_simplify,
)
from ..data.pdp import (
    pdp_yue_hant_hk,
    pdp_yue_hant_hk_flatten,
    pdp_yue_hant_hk_simplify,
)
from ..data.t import (
    t_cmn_hans_hk,
    t_cmn_hans_hk_flatten,
    t_cmn_hant_hk,
    t_cmn_hant_hk_simplify,
)


def _test_get_hanzi_flattened(series: Series, expected: Series):
    output = get_hanzi_flattened(series)
    assert len(series.events) == len(output.events)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output.events, expected.events), 1):
        if event.text.count("\n") != 0:
            errors.append(f"Subtitle {i} contains newline")
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


def _test_get_hanzi_simplified(series: Series, expected: Series = None):
    output = get_hanzi_simplified(series)
    assert len(series.events) == len(output.events)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output.events, expected.events), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


# get_hanzi_flattened
def test_get_hanzi_flattened_kob(
    kob_yue_hans_hk: Series, kob_yue_hans_hk_flatten: Series
):
    _test_get_hanzi_flattened(kob_yue_hans_hk, kob_yue_hans_hk_flatten)


def test_get_hanzi_flattened_mnt(
    mnt_cmn_hant_hk: Series, mnt_cmn_hant_hk_flatten: Series
):
    _test_get_hanzi_flattened(mnt_cmn_hant_hk, mnt_cmn_hant_hk_flatten)


def test_get_hanzi_flattened_pdp(
    pdp_yue_hant_hk: Series, pdp_yue_hant_hk_flatten: Series
):
    _test_get_hanzi_flattened(pdp_yue_hant_hk, pdp_yue_hant_hk_flatten)


def test_get_hanzi_flattened_t(t_cmn_hans_hk: Series, t_cmn_hans_hk_flatten: Series):
    _test_get_hanzi_flattened(t_cmn_hans_hk, t_cmn_hans_hk_flatten)


# get_hanzi_simplified
def test_get_hanzi_simplified_kob(
    kob_yue_hant_hk: Series, kob_yue_hant_hk_simplify: Series
):
    _test_get_hanzi_simplified(kob_yue_hant_hk, kob_yue_hant_hk_simplify)


def test_get_hanzi_simplified_mnt(
    mnt_cmn_hant_hk: Series, mnt_cmn_hant_hk_simplify: Series
):
    _test_get_hanzi_simplified(mnt_cmn_hant_hk, mnt_cmn_hant_hk_simplify)


def test_get_hanzi_simplified_pdp(
    pdp_yue_hant_hk: Series, pdp_yue_hant_hk_simplify: Series
):
    _test_get_hanzi_simplified(pdp_yue_hant_hk, pdp_yue_hant_hk_simplify)


def test_get_hanzi_simplified_t(t_cmn_hant_hk: Series, t_cmn_hant_hk_simplify: Series):
    _test_get_hanzi_simplified(t_cmn_hant_hk, t_cmn_hant_hk_simplify)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("你好世界", "你好世界"),
    ],
)
def test_get_hanzi_text_simplified(text: str, expected: str):
    assert _get_hanzi_text_simplified(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("line 1\nline 2", "line 1　line 2"),
    ],
)
def test_get_hanzi_text_flattened(text: str, expected: str):
    assert _get_hanzi_text_flattened(text) == expected
