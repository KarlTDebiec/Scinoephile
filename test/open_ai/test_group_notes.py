#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for OpenAI Service."""
from __future__ import annotations

from pprint import pformat

import pytest

from scinoephile.core import SubtitleSeries
from scinoephile.core.subtitles import get_pair_with_zero_start, get_series_pair_strings
from scinoephile.open_ai import (
    OpenAiService,
)
from scinoephile.testing import SyncTestCase
from ..data.mnt import mnt_input_english, mnt_input_hanzi, mnt_test_cases


@pytest.fixture
def openai_service():
    return OpenAiService()


@pytest.mark.parametrize("test_case", mnt_test_cases)
def test_group_notes(
    openai_service: OpenAiService,
    mnt_input_hanzi: SubtitleSeries,
    mnt_input_english: SubtitleSeries,
    test_case: SyncTestCase,
) -> None:

    hanzi_block = mnt_input_hanzi.slice(test_case.hanzi_start, test_case.hanzi_end)
    english_block = mnt_input_english.slice(
        test_case.english_start, test_case.english_end
    )
    hanzi_block, english_block = get_pair_with_zero_start(hanzi_block, english_block)
    hanzi_str, english_str = get_series_pair_strings(hanzi_block, english_block)

    notes = openai_service.get_sync_notes_yat(hanzi_block, english_block)

    print(f"CHINESE:\n{hanzi_str}\n")
    print(f"ENGLISH:\n{english_str}\n")
    print(f"Received Chinese notes:\n{pformat(notes.chinese,width=120)}\n")
    print(f"Received English notes:\n{pformat(notes.english,width=120)}\n")

    assert len(hanzi_block) == len(notes.chinese)
    assert len(english_block) == len(notes.english)

    group_notes = openai_service.get_synchronization_group_notes(
        hanzi_block, english_block, notes
    )

    print(f"Received Group notes:\n{pformat(group_notes.groups,width=120)}\n")
    print(
        f"Expected synchronization:\n{pformat(test_case.expected_sync_response.synchronization,width=120)}\n"
    )

    assert len(test_case.expected_sync_response.synchronization) == len(
        group_notes.groups
    )
