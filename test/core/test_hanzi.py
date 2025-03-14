#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.hanzi."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.hanzi import (
    _get_hanzi_text_flattened,  # noqa
    _get_hanzi_text_simplified,  # noqa
    get_hanzi_cleaned,
    get_hanzi_flattened,
    get_hanzi_simplified,
)
from ..data.kob import (
    kob_yue_hans,
    kob_yue_hans_clean,
    kob_yue_hans_flatten,
    kob_yue_hant,
    kob_yue_hant_simplify,
)
from ..data.mnt import (
    mnt_zho_hant,
    mnt_zho_hant_clean,
    mnt_zho_hant_flatten,
    mnt_zho_hant_simplify,
)
from ..data.pdp import (
    pdp_yue_hant,
    pdp_yue_hant_clean,
    pdp_yue_hant_flatten,
    pdp_yue_hant_simplify,
)
from ..data.t import (
    t_zho_hans,
    t_zho_hans_clean,
    t_zho_hans_flatten,
    t_zho_hant,
    t_zho_hant_simplify,
)


# region Implementations
def _test_get_hanzi_cleaned(series: Series, expected: Series):
    output = get_hanzi_cleaned(series)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output.events, expected.events), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


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


# endregion


# region get_hanzi_cleaned
def test_get_hanzi_cleaned_kob(kob_yue_hans: Series, kob_yue_hans_clean: Series):
    _test_get_hanzi_cleaned(kob_yue_hans, kob_yue_hans_clean)


def test_get_hanzi_cleaned_mnt(mnt_zho_hant: Series, mnt_zho_hant_clean: Series):
    _test_get_hanzi_cleaned(mnt_zho_hant, mnt_zho_hant_clean)


def test_get_hanzi_cleaned_pdp(pdp_yue_hant: Series, pdp_yue_hant_clean: Series):
    _test_get_hanzi_cleaned(pdp_yue_hant, pdp_yue_hant_clean)


def test_get_hanzi_cleaned_t(t_zho_hans: Series, t_zho_hans_clean: Series):
    _test_get_hanzi_cleaned(t_zho_hans, t_zho_hans_clean)


# endregion


# region get_hanzi_flattened
def test_get_hanzi_flattened_kob(kob_yue_hans: Series, kob_yue_hans_flatten: Series):
    _test_get_hanzi_flattened(kob_yue_hans, kob_yue_hans_flatten)


def test_get_hanzi_flattened_mnt(mnt_zho_hant: Series, mnt_zho_hant_flatten: Series):
    _test_get_hanzi_flattened(mnt_zho_hant, mnt_zho_hant_flatten)


def test_get_hanzi_flattened_pdp(pdp_yue_hant: Series, pdp_yue_hant_flatten: Series):
    _test_get_hanzi_flattened(pdp_yue_hant, pdp_yue_hant_flatten)


def test_get_hanzi_flattened_t(t_zho_hans: Series, t_zho_hans_flatten: Series):
    _test_get_hanzi_flattened(t_zho_hans, t_zho_hans_flatten)


# endregion


# region get_hanzi_simplified
def test_get_hanzi_simplified_kob(kob_yue_hant: Series, kob_yue_hant_simplify: Series):
    _test_get_hanzi_simplified(kob_yue_hant, kob_yue_hant_simplify)


def test_get_hanzi_simplified_mnt(mnt_zho_hant: Series, mnt_zho_hant_simplify: Series):
    _test_get_hanzi_simplified(mnt_zho_hant, mnt_zho_hant_simplify)


def test_get_hanzi_simplified_pdp(pdp_yue_hant: Series, pdp_yue_hant_simplify: Series):
    _test_get_hanzi_simplified(pdp_yue_hant, pdp_yue_hant_simplify)


def test_get_hanzi_simplified_t(t_zho_hant: Series, t_zho_hant_simplify: Series):
    _test_get_hanzi_simplified(t_zho_hant, t_zho_hant_simplify)


# endregion


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
