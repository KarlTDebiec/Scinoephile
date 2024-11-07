#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for OpenAI Service."""
from __future__ import annotations

import pytest

from data.mnt import mnt_test_cases
from scinoephile.core import ScinoephileException, SubtitleSeries
from scinoephile.synchronization import SynchronizationService
from scinoephile.testing import SyncTestCase
from ..data.mnt import mnt_input_english, mnt_input_hanzi


@pytest.fixture
def synchronization_service():
    return SynchronizationService()


@pytest.mark.parametrize("test_case", mnt_test_cases)
def test_get_synced_short(
    synchronization_service: SynchronizationService,
    mnt_input_hanzi: SubtitleSeries,
    mnt_input_english: SubtitleSeries,
    test_case: SyncTestCase,
) -> None:
    hanzi = mnt_input_hanzi.slice(test_case.hanzi_start, test_case.hanzi_end)
    english = mnt_input_english.slice(test_case.english_start, test_case.english_end)
    hanzi_str = hanzi.to_string("srt")
    english_str = english.to_string("srt")
    output = f"CHINESE:\n{hanzi_str}\nENGLISH:\n{english_str}\n"

    try:
        bilingual = synchronization_service.get_synced_short(hanzi, english)
    except ScinoephileException as e:
        print(output)
        raise ScinoephileException(output) from e

    bilingual_str = bilingual.to_string("srt")
    output += f"BILINGUAL:\n{bilingual_str}\n"
    print(output)
