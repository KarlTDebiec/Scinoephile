#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.synchronization."""

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.pairs import get_pair_strings
from scinoephile.core.synchronization import (
    get_overlap_string,
    get_sync_groups,
    get_sync_groups_string,
    get_sync_overlap_matrix,
    get_synced_series,
    get_synced_series_from_groups,
)
from scinoephile.testing import SyncTestCase
from test.data.mnt import mnt_sync_test_cases  # noqa: F401
from test.data.pdp import pdp_sync_test_cases  # noqa: F401


def _test_blocks(one: Series, two: Series, test_case: SyncTestCase):
    """Test synchronization blocks.

    Arguments:
        one: series one with which to test
        two: series two with which to test
        test_case: indexes for slicing input block and expected output for validation
    """
    print()

    # Get and print subtitles
    one_block = one.slice(test_case.one_start, test_case.one_end)
    two_block = two.slice(test_case.two_start, test_case.two_end)
    one_str, two_str = get_pair_strings(one_block, two_block)
    print(f"ONE ({test_case.one_start + 1} - {test_case.one_end}):\n{one_str}")
    print(f"TWO ({test_case.two_start + 1} - {test_case.two_end}):\n{two_str}")

    # Get and print overlap matrix
    overlap = get_sync_overlap_matrix(one_block, two_block)
    print(f"OVERLAP: {get_overlap_string(overlap)}")

    # Get and print sync groups
    sync_groups = get_sync_groups(one_block, two_block)
    print(f"SYNC GROUPS:\n{get_sync_groups_string(sync_groups)}")

    assert sync_groups == test_case.sync_groups

    # Get and print synced series
    series = get_synced_series_from_groups(one_block, two_block, sync_groups)
    print(f"SYNCED SUBTITLES:\n{series.to_simple_string()}")


def _test_get_synced_series(one: Series, two: Series, expected: Series):
    """Test get_synced_series.

    Arguments:
        one: series one with which to test
        two: series two with which to test
        expected: expected output series
    """
    bilingual = get_synced_series(one, two)
    assert len(bilingual) == len(expected)

    errors = []
    for i, (event, expected_event) in enumerate(zip(bilingual, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


# blocks
@pytest.mark.parametrize("test_case", mnt_sync_test_cases)
def test_blocks_mnt(
    mnt_zho_hant_clean_flatten_simplify: Series,
    mnt_eng_clean_flatten: Series,
    test_case: SyncTestCase,
):
    """Test synchronization blocks for MNT.

    Arguments:
        mnt_zho_hant_clean_flatten_simplify: MNT 繁体中文 series fixture
        mnt_eng_clean_flatten: MNT English series fixture
        test_case: Indexes for slicing input block and expected output for validation
    """
    _test_blocks(mnt_zho_hant_clean_flatten_simplify, mnt_eng_clean_flatten, test_case)


@pytest.mark.parametrize("test_case", pdp_sync_test_cases)
def test_blocks_pdp(
    pdp_yue_hant_clean_flatten_simplify: Series,
    pdp_eng_clean_flatten: Series,
    test_case: SyncTestCase,
):
    """Test synchronization blocks for PDP.

    Arguments:
        pdp_yue_hant_clean_flatten_simplify: PDP 繁体粤文 series fixture
        pdp_eng_clean_flatten: PDP English series fixture
        test_case: Indexes for slicing input block and expected output for validation
    """
    _test_blocks(pdp_yue_hant_clean_flatten_simplify, pdp_eng_clean_flatten, test_case)


# get_synced_series
def test_get_synced_series_mnt(
    mnt_zho_hant_clean_flatten_simplify: Series,
    mnt_eng_clean_flatten: Series,
    mnt_zho_hans_eng: Series,
):
    """Test get_synced_series with MNT.

    Arguments:
        mnt_zho_hant_clean_flatten_simplify: MNT 繁体中文 series fixture
        mnt_eng_clean_flatten: MNT English series fixture
        mnt_zho_hans_eng: Expected output bilingual series fixture
    """
    _test_get_synced_series(
        mnt_zho_hant_clean_flatten_simplify,
        mnt_eng_clean_flatten,
        mnt_zho_hans_eng,
    )


def test_get_synced_series_pdp(
    pdp_yue_hant_clean_flatten_simplify: Series,
    pdp_eng_clean_flatten: Series,
    pdp_yue_hans_eng: Series,
):
    """Test get_synced_series with PDP.

    Arguments:
        pdp_yue_hant_clean_flatten_simplify: PDP 繁体粤文 series fixture
        pdp_eng_clean_flatten: PDP English series fixture
        pdp_yue_hans_eng: Expected output bilingual series fixture
    """
    _test_get_synced_series(
        pdp_yue_hant_clean_flatten_simplify,
        pdp_eng_clean_flatten,
        pdp_yue_hans_eng,
    )
