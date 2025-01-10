#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.synchronization."""
from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.pairs import get_pair_strings
from scinoephile.core.synchronization import (
    get_sync_groups,
    get_sync_overlap_matrix,
    get_synced_series,
    get_synced_series_from_groups,
)
from scinoephile.testing import SyncTestCase
from ..data.mnt import (
    mnt_cmn_hans_hk_en_us,
    mnt_cmn_hant_hk_flatten_simplify,
    mnt_en_us_clean_flatten,
    mnt_test_cases,
)
from ..data.pdp import (
    pdp_en_hk_clean_flatten,
    pdp_test_cases,
    pdp_yue_hans_hk_en_hk,
    pdp_yue_hant_hk_flatten_simplify,
)


def _test_blocks(hanzi: Series, english: Series, test_case: SyncTestCase):
    hanzi_block = hanzi.slice(test_case.hanzi_start, test_case.hanzi_end)
    english_block = english.slice(test_case.english_start, test_case.english_end)

    hanzi_str, english_str = get_pair_strings(hanzi_block, english_block)
    # print(f"\nCHINESE:\n{hanzi_str}")
    # print(f"\nENGLISH:\n{english_str}")

    overlap = get_sync_overlap_matrix(hanzi_block, english_block)
    # print("\nOVERLAP:")
    # print(get_overlap_string(overlap))

    sync_groups = get_sync_groups(hanzi_block, english_block)
    # print(f"\nSYNC GROUPS:\n{pformat(sync_groups, width=120)}")

    assert sync_groups == test_case.sync_groups

    series = get_synced_series_from_groups(hanzi_block, english_block, sync_groups)
    # print(f"\nSYNCED SUBTITLES:\n{series.to_simple_string()}")


def _test_get_synced_series(hanzi: Series, english: Series, expected: Series):
    bilingual = get_synced_series(hanzi, english)
    assert len(bilingual.events) == len(expected.events)

    errors = []
    for i, (event, expected_event) in enumerate(
        zip(bilingual.events, expected.events), 1
    ):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


# blocks
@pytest.mark.parametrize("test_case", mnt_test_cases)
def test_blocks_mnt(
    mnt_cmn_hant_hk_flatten_simplify: Series,
    mnt_en_us_clean_flatten: Series,
    test_case: SyncTestCase,
):
    _test_blocks(mnt_cmn_hant_hk_flatten_simplify, mnt_en_us_clean_flatten, test_case)


@pytest.mark.parametrize("test_case", pdp_test_cases)
def test_blocks_pdp(
    pdp_yue_hant_hk_flatten_simplify: Series,
    pdp_en_hk_clean_flatten: Series,
    test_case: SyncTestCase,
):
    _test_blocks(pdp_yue_hant_hk_flatten_simplify, pdp_en_hk_clean_flatten, test_case)


# get_synced_series
def test_get_synced_series_mnt(
    mnt_cmn_hant_hk_flatten_simplify: Series,
    mnt_en_us_clean_flatten: Series,
    mnt_cmn_hans_hk_en_us: Series,
):
    _test_get_synced_series(
        mnt_cmn_hant_hk_flatten_simplify, mnt_en_us_clean_flatten, mnt_cmn_hans_hk_en_us
    )


def test_get_synced_series_pdp(
    pdp_yue_hant_hk_flatten_simplify: Series,
    pdp_en_hk_clean_flatten: Series,
    pdp_yue_hans_hk_en_hk: Series,
):
    _test_get_synced_series(
        pdp_yue_hant_hk_flatten_simplify, pdp_en_hk_clean_flatten, pdp_yue_hans_hk_en_hk
    )
