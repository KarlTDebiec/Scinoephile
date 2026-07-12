#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for delineation test cases used during Yue/Zho alignment."""

from __future__ import annotations

from unittest.mock import Mock

from pydub import AudioSegment

from scinoephile.audio.subtitles import AudioSeries, AudioSubtitle
from scinoephile.core.llms import Queryer
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.delineation import DelineationPrompt, DelineationTestCase
from scinoephile.multilang.yue_zho.transcription.aligner import Aligner
from scinoephile.multilang.yue_zho.transcription.alignment import Alignment

_LOCALIZED_PROMPT = DelineationPrompt(
    src_1_sub_1="cankao_yi",
    src_1_sub_2="cankao_er",
    src_2_sub_1="mubiao_yi",
    src_2_sub_2="mubiao_er",
    src_2_sub_1_shifted="shuchu_yi",
    src_2_sub_2_shifted="shuchu_er",
)
"""Delineation prompt using non-default correspondence field names."""


def _get_alignment() -> Alignment:
    """Get a two-group alignment that can shift target text."""
    zhongwen = Series(
        events=[
            Subtitle(start=0, end=1000, text="參考一"),
            Subtitle(start=1000, end=2000, text="參考二"),
        ],
    )
    yuewen = AudioSeries(
        audio=AudioSegment.silent(duration=2000),
        events=[
            AudioSubtitle(start=0, end=1000, text="甲"),
            AudioSubtitle(start=1000, end=2000, text="乙"),
        ],
    )
    alignment = Alignment(zhongwen, yuewen)
    alignment._sync_groups_override = [([0], [0]), ([1], [1])]
    return alignment


def test_alignment_constructs_semantic_fields_with_configured_prompt():
    """Alignment should construct semantic fields using the provided prompt aliases."""
    alignment = _get_alignment()

    test_case = alignment.get_delineation_test_case(0, _LOCALIZED_PROMPT)

    assert test_case is not None
    assert isinstance(test_case, DelineationTestCase)
    assert test_case.prompt is _LOCALIZED_PROMPT
    assert test_case.query.model_dump() == {
        "reference_one": "參考一",
        "reference_two": "參考二",
        "target_one": "甲",
        "target_two": "乙",
    }
    assert test_case.query.model_dump(by_alias=True) == {
        "cankao_yi": "參考一",
        "cankao_er": "參考二",
        "mubiao_yi": "甲",
        "mubiao_er": "乙",
    }


def test_aligner_uses_queryer_prompt_and_semantic_shift_output():
    """Aligner should propagate its prompt and consume semantic answer fields."""
    alignment = _get_alignment()
    delineation_queryer = Mock(spec=Queryer)
    delineation_queryer.prompt = _LOCALIZED_PROMPT

    def add_answer(test_case: DelineationTestCase) -> DelineationTestCase:
        """Move the second target subtitle into the first sync group."""
        return type(test_case).model_validate(
            {
                **test_case.model_dump(),
                "answer": {"output_one": "甲乙"},
            }
        )

    delineation_queryer.side_effect = add_answer
    aligner = Aligner(
        delineation_queryer=delineation_queryer,
        punctuation_queryer=Mock(spec=Queryer),
    )

    restart_required = aligner._delineate(alignment)

    encountered = delineation_queryer.call_args.args[0]
    assert encountered.prompt is _LOCALIZED_PROMPT
    assert not restart_required
    assert alignment.sync_groups == [([0], [0, 1]), ([1], [])]
