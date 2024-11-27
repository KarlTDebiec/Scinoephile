#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for OpenAI Service."""
from __future__ import annotations

from pprint import pformat

import pytest

from scinoephile.core import Series
from scinoephile.core.pairs import get_pair_strings, get_pair_with_zero_start
from scinoephile.open_ai import (
    OpenAiService,
)
from scinoephile.open_ai.functions import (
    get_sync_from_sync_groups,
    get_sync_groups_from_indexes,
    get_sync_indexes_from_notes,
    get_sync_overlap_notes,
)
from scinoephile.testing import SyncTestCase
from scinoephile.testing.mark import skip_if_ci
from ..data.mnt import mnt_cmn_hant_hk, mnt_en_us, mnt_test_cases


@pytest.fixture
def open_ai_service():
    return OpenAiService()


@skip_if_ci()
@pytest.mark.parametrize(
    "test_case, language",
    [(case, lang) for case in mnt_test_cases for lang in ["chinese", "english"]],
)
def test_get_sync_notes(
    open_ai_service: OpenAiService,
    mnt_cmn_hant_hk: Series,
    mnt_en_us: Series,
    test_case: SyncTestCase,
    language: str,
) -> None:
    hanzi_block = mnt_cmn_hant_hk.slice(test_case.hanzi_start, test_case.hanzi_end)
    english_block = mnt_en_us.slice(test_case.english_start, test_case.english_end)
    hanzi_block, english_block = get_pair_with_zero_start(hanzi_block, english_block)
    hanzi_str, english_str = get_pair_strings(hanzi_block, english_block)
    output = f"CHINESE:\n{hanzi_str}\nENGLISH:\n{english_str}\n"

    overlap_notes = get_sync_overlap_notes(hanzi_block, english_block, language)
    output += f"OVERLAP NOTES:\n{pformat(overlap_notes, width=120)}\n"

    notes = open_ai_service.get_sync_notes(hanzi_block, english_block, language)
    notes_dict = notes.model_dump()
    output += f"NOTES:\n{pformat(notes_dict, width=120)}\n"

    if language == "english":
        assert len(notes_dict) == len(english_block), output
    elif language == "chinese":
        assert len(notes_dict) == len(hanzi_block), output

    mapping = get_sync_indexes_from_notes(notes_dict)
    output += f"MAPPING:\n{pformat(mapping, width=120)}\n"

    if language == "english":
        assert len(mapping) == len(english_block), output
    elif language == "chinese":
        assert len(mapping) == len(hanzi_block), output

    groups = get_sync_groups_from_indexes(mapping)

    sync = get_sync_from_sync_groups(groups, "chinese", len(hanzi_block.events))
    output += f"SYNC:\n{pformat(sync, width=120)}\n"

    expected = test_case.sync_groups.synchronization
    output += f"EXPECTED:\n{pformat(expected, width=120)}\n"

    print(output)
    assert sync == test_case.sync_groups.synchronization, output
