#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for punctuation test cases used during Yue/Zho alignment."""

from __future__ import annotations

from unittest.mock import Mock

from pydub import AudioSegment
from pytest import MonkeyPatch

from scinoephile.audio.subtitles import AudioSeries, AudioSubtitle
from scinoephile.core.llms import Queryer
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.punctuation import PunctuationPrompt
from scinoephile.multilang.yue_zho.transcription import aligner as aligner_module
from scinoephile.multilang.yue_zho.transcription.aligner import Aligner
from scinoephile.multilang.yue_zho.transcription.alignment import Alignment
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YueZhoPunctuationTestCase,
)

_LOCALIZED_PROMPT = PunctuationPrompt(
    src_1="zimu",
    src_2="cankao",
    output="jieguo",
)
"""Punctuation prompt using non-default correspondence field names."""


def _get_alignment() -> Alignment:
    """Get a one-group alignment that requires punctuation."""
    zhongwen = Series(
        events=[Subtitle(start=0, end=1000, text="你好！")],
    )
    yuewen = AudioSeries(
        audio=AudioSegment.silent(duration=1000),
        events=[AudioSubtitle(start=0, end=1000, text="你好")],
    )
    alignment = Alignment(zhongwen, yuewen)
    alignment._sync_groups_override = [([0], [0])]
    return alignment


def _get_merged_subtitle(
    subtitles: list[AudioSubtitle],
    *,
    text: str | None = None,
) -> AudioSubtitle:
    """Get a merged subtitle without requiring transcription segment fixtures."""
    if text is None:
        text = "".join(subtitle.text for subtitle in subtitles)
    return AudioSubtitle(
        start=subtitles[0].start,
        end=subtitles[-1].end,
        text=text,
    )


def test_alignment_constructs_semantic_fields_with_configured_prompt():
    """Alignment should construct semantic fields using the provided prompt aliases."""
    alignment = _get_alignment()

    test_case = alignment.get_punctuation_test_case(0, _LOCALIZED_PROMPT)

    assert test_case is not None
    assert isinstance(test_case, YueZhoPunctuationTestCase)
    assert test_case.prompt is _LOCALIZED_PROMPT
    assert test_case.query.model_dump() == {
        "subtitles": ["你好"],
        "guide": "你好！",
    }
    assert test_case.query.model_dump(by_alias=True) == {
        "zimu": ["你好"],
        "cankao": "你好！",
    }


def test_aligner_uses_queryer_prompt_and_semantic_output(monkeypatch: MonkeyPatch):
    """Aligner should propagate its prompt and consume semantic answer output."""
    alignment = _get_alignment()
    punctuation_queryer = Mock(spec=Queryer)
    punctuation_queryer.prompt = _LOCALIZED_PROMPT

    def add_answer(
        test_case: YueZhoPunctuationTestCase,
    ) -> YueZhoPunctuationTestCase:
        """Add a valid punctuation answer to a test case."""
        result = type(test_case).model_validate(
            {
                **test_case.model_dump(),
                "answer": {"output": "你好！"},
            }
        )
        return result

    punctuation_queryer.side_effect = add_answer
    monkeypatch.setattr(aligner_module, "get_sub_merged", _get_merged_subtitle)
    aligner = Aligner(
        delineation_queryer=Mock(spec=Queryer),
        punctuation_queryer=punctuation_queryer,
    )

    aligner._punctuate(alignment)

    encountered = punctuation_queryer.call_args.args[0]
    assert encountered.prompt is _LOCALIZED_PROMPT
    assert alignment.yuewen[0].text == "你好！"


def test_aligner_falls_back_to_concatenation_after_invalid_answer(
    monkeypatch: MonkeyPatch,
):
    """A rejected answer should retain the existing concatenation fallback."""
    alignment = _get_alignment()
    punctuation_queryer = Mock(spec=Queryer)
    punctuation_queryer.prompt = _LOCALIZED_PROMPT

    def reject_answer(
        test_case: YueZhoPunctuationTestCase,
    ) -> YueZhoPunctuationTestCase:
        """Attempt to add an answer that changes subtitle characters."""
        result = type(test_case).model_validate(
            {
                **test_case.model_dump(),
                "answer": {"output": "你壞"},
            }
        )
        return result

    punctuation_queryer.side_effect = reject_answer
    monkeypatch.setattr(aligner_module, "get_sub_merged", _get_merged_subtitle)
    aligner = Aligner(
        delineation_queryer=Mock(spec=Queryer),
        punctuation_queryer=punctuation_queryer,
    )

    aligner._punctuate(alignment)

    assert alignment.yuewen[0].text == "你好"
