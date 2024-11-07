#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for scinoephile.core.synchronization"""
from __future__ import annotations

from pprint import pformat

import numpy as np
import pytest

from scinoephile.core import SubtitleSeries
from scinoephile.core.pairs import get_pair_strings
from scinoephile.core.synchronization import get_sync_groups, get_sync_overlap_matrix
from scinoephile.testing import SyncTestCase
from ..data.mnt import mnt_input_english, mnt_input_hanzi, mnt_test_cases


@pytest.mark.parametrize("test_case", mnt_test_cases)
def test_get_sync_overlap_matrix(
    mnt_input_hanzi: SubtitleSeries,
    mnt_input_english: SubtitleSeries,
    test_case: SyncTestCase,
) -> None:
    hanzi = mnt_input_hanzi.slice(test_case.hanzi_start, test_case.hanzi_end)
    english = mnt_input_english.slice(test_case.english_start, test_case.english_end)
    hanzi_str, english_str = get_pair_strings(hanzi, english)

    hanzi_to_english_overlap = get_sync_overlap_matrix(hanzi, english)
    english_to_hanzi_overlap = get_sync_overlap_matrix(english, hanzi)
    print()
    print("CHINESE:")
    print(hanzi_str)
    print()
    print("ENGLISH:")
    print(english_str)
    print()
    print("CHINESE TO ENGLISH OVERLAP:")
    print(np.array2string(hanzi_to_english_overlap, precision=2, suppress_small=True))
    print()
    print("ENGLISH TO CHINESE OVERLAP:")
    print(np.array2string(english_to_hanzi_overlap, precision=2, suppress_small=True))

    sam = get_sync_groups(hanzi, english)
    print()
    print("SYNC GROUPS:")
    print(pformat(sam, width=120))
