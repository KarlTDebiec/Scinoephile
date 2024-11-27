#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for scinoephile.core.synchronization"""
from __future__ import annotations

from pprint import pformat

import pytest

from scinoephile.core import Series
from scinoephile.core.pairs import get_pair_strings
from scinoephile.core.synchronization import (
    get_overlap_string,
    get_sync_groups,
    get_sync_overlap_matrix,
    get_synced_series,
    get_synced_series_from_groups,
)
from scinoephile.testing import SyncTestCase
from ..data.mnt import mnt_input_english, mnt_input_hanzi, mnt_test_cases
from ..data.pdp import (
    pdp_output_en_clean_merge,
    pdp_output_yue_hant_merge,
    pdp_test_cases,
)


def _test_blocks(input_hanzi: Series, input_english: Series, test_case: SyncTestCase):
    hanzi = input_hanzi.slice(test_case.hanzi_start, test_case.hanzi_end)
    english = input_english.slice(test_case.english_start, test_case.english_end)

    hanzi_str, english_str = get_pair_strings(hanzi, english)
    print(f"\nCHINESE:\n{hanzi_str}")
    print(f"\nENGLISH:\n{english_str}")

    overlap = get_sync_overlap_matrix(hanzi, english)
    print("\nOVERLAP:")
    print(get_overlap_string(overlap))

    sync_groups = get_sync_groups(hanzi, english)
    print(f"\nSYNC GROUPS:\n{pformat(sync_groups, width=120)}")

    assert sync_groups == test_case.sync_groups

    series = get_synced_series_from_groups(hanzi, english, sync_groups)
    print(f"\nSYNCED SUBTITLES:\n{series.to_simple_string()}")


def _test_complete(hanzi: Series, english: Series, expected_length: int):
    bilingual = get_synced_series(hanzi, english)
    print(bilingual.to_string("srt"))
    assert len(bilingual) == expected_length


@pytest.mark.parametrize("test_case", mnt_test_cases)
def test_blocks_mnt(
    mnt_input_hanzi: Series,
    mnt_input_english: Series,
    test_case: SyncTestCase,
):
    _test_blocks(mnt_input_hanzi, mnt_input_english, test_case)


@pytest.mark.parametrize("test_case", pdp_test_cases)
def test_blocks_pdp(
    pdp_output_yue_hant_merge: Series,
    pdp_output_en_clean_merge: Series,
    test_case: SyncTestCase,
):
    _test_blocks(pdp_output_yue_hant_merge, pdp_output_en_clean_merge, test_case)


def test_complete_mnt(
    mnt_input_hanzi: Series,
    mnt_input_english: Series,
):
    _test_complete(mnt_input_hanzi, mnt_input_english, 733)


def test_complete_pdp(
    pdp_output_yue_hant_merge: Series,
    pdp_output_en_clean_merge: Series,
):
    _test_complete(pdp_output_yue_hant_merge, pdp_output_en_clean_merge, 559)
