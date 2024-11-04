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
def test_notes_english(
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

    notes = openai_service.get_sync_notes_eee(hanzi_block, english_block, "english")
    notes_dict = notes.model_dump()

    print(f"CHINESE:\n{hanzi_str}\n")
    print(f"ENGLISH:\n{english_str}\n")
    print(f"NOTES:\n{pformat(notes_dict,width=120)}\n")

    assert len(notes_dict) == len(english_block)
