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
from scinoephile.open_ai.functions import (
    get_sync_from_sync_groups,
    get_sync_groups_from_indexes,
    get_sync_indexes_from_notes,
)
from scinoephile.testing import SyncTestCase
from ..data.mnt import mnt_input_english, mnt_input_hanzi, mnt_test_cases


@pytest.fixture
def openai_service():
    return OpenAiService()


@pytest.mark.parametrize(
    "test_case, language",
    [(case, lang) for case in mnt_test_cases for lang in ["chinese", "english"]],
)
def test_get_sync_notes(
    openai_service: OpenAiService,
    mnt_input_hanzi: SubtitleSeries,
    mnt_input_english: SubtitleSeries,
    test_case: SyncTestCase,
    language: str,
) -> None:
    hanzi_block = mnt_input_hanzi.slice(test_case.hanzi_start, test_case.hanzi_end)
    english_block = mnt_input_english.slice(
        test_case.english_start, test_case.english_end
    )
    hanzi_block, english_block = get_pair_with_zero_start(hanzi_block, english_block)
    hanzi_str, english_str = get_series_pair_strings(hanzi_block, english_block)

    notes = openai_service.get_sync_notes(hanzi_block, english_block, language)
    notes_dict = notes.model_dump()

    print(f"CHINESE:\n{hanzi_str}\n")
    print(f"ENGLISH:\n{english_str}\n")
    print(f"{language.upper()} NOTES:\n{pformat(notes_dict, width=120)}\n")

    if language == "english":
        assert len(notes_dict) == len(english_block)
    elif language == "chinese":
        assert len(notes_dict) == len(hanzi_block)

    mapping = get_sync_indexes_from_notes(notes_dict)
    print(f"MAPPING:\n{pformat(mapping, width=120)}\n")

    if language == "english":
        assert len(mapping) == len(english_block)
    elif language == "chinese":
        assert len(mapping) == len(hanzi_block)

    groups = get_sync_groups_from_indexes(mapping)

    sync = get_sync_from_sync_groups(groups, "chinese", len(hanzi_block.events))
    print(f"RECIEVED SYNC:\n{pformat(sync, width=120)}\n")
    print(
        f"EXPECTED SYNC:\n{pformat(test_case.expected_sync_response.synchronization, width=120)}\n"
    )

    assert sync == test_case.expected_sync_response.synchronization
