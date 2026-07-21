#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for delineation test cases used during transcription alignment."""

from __future__ import annotations

from unittest.mock import Mock, patch

from pydub import AudioSegment

from scinoephile.audio.subtitles import AudioSeries, AudioSubtitle
from scinoephile.core.llms import Queryer
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.transcription.aligner import TranscriptionAligner
from scinoephile.lang.transcription.alignment import TranscriptionAlignment
from scinoephile.llms.delineation import DelineationPrompt, DelineationTestCase

_LOCALIZED_PROMPT = DelineationPrompt(
    ref_sub_1="cankao_yi",
    ref_sub_2="cankao_er",
    target_sub_1="mubiao_yi",
    target_sub_2="mubiao_er",
    target_sub_1_shifted="shuchu_yi",
    target_sub_2_shifted="shuchu_er",
)
"""Delineation prompt using non-default correspondence field names."""


def _get_alignment() -> TranscriptionAlignment:
    """Get a two-group alignment that can shift target text."""
    reference = Series(
        events=[
            Subtitle(start=0, end=1000, text="參考一"),
            Subtitle(start=1000, end=2000, text="參考二"),
        ],
    )
    transcription = AudioSeries(
        audio=AudioSegment.silent(duration=2000),
        events=[
            AudioSubtitle(start=0, end=1000, text="甲"),
            AudioSubtitle(start=1000, end=2000, text="乙"),
        ],
    )
    alignment = TranscriptionAlignment(reference, transcription)
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
    aligner = TranscriptionAligner(
        delineation_queryer=delineation_queryer,
        punctuation_queryer=Mock(spec=Queryer),
    )

    restart_required = aligner._delineate(alignment)

    encountered = delineation_queryer.call_args.args[0]
    assert encountered.prompt is _LOCALIZED_PROMPT
    assert restart_required
    assert alignment.sync_groups == [([0], [0, 1]), ([1], [])]


def test_aligner_restarts_to_propagate_text_across_multiple_boundaries():
    """Aligner should revisit earlier boundaries after shifting whole subtitles."""
    reference = Series(
        events=[
            Subtitle(start=0, end=1000, text="參考一"),
            Subtitle(start=1000, end=2000, text="參考二"),
            Subtitle(start=2000, end=3000, text="參考三"),
        ],
    )
    transcription = AudioSeries(
        audio=AudioSegment.silent(duration=3000),
        events=[
            AudioSubtitle(start=0, end=1000, text="甲"),
            AudioSubtitle(start=1000, end=2000, text="乙"),
            AudioSubtitle(start=2000, end=3000, text="丙"),
        ],
    )
    alignment = TranscriptionAlignment(reference, transcription)
    alignment._sync_groups_override = [([0], [0]), ([1], [1]), ([2], [2])]
    delineation_queryer = Mock(spec=Queryer)
    delineation_queryer.prompt = _LOCALIZED_PROMPT

    def shift_left(test_case: DelineationTestCase) -> DelineationTestCase:
        """Move text leftward until all targets reach the first group."""
        answer: dict[str, str] = {}
        if test_case.query.target_one == "乙":
            answer = {"output_one": "乙丙"}
        elif test_case.query.target_two == "乙丙":
            answer = {"output_one": "甲乙丙"}
        return type(test_case).model_validate(
            {
                **test_case.model_dump(),
                "answer": answer,
            }
        )

    delineation_queryer.side_effect = shift_left
    aligner = TranscriptionAligner(
        delineation_queryer=delineation_queryer,
        punctuation_queryer=Mock(spec=Queryer),
    )

    while aligner._delineate(alignment):
        pass

    assert alignment.sync_groups == [([0], [0, 1, 2]), ([1], []), ([2], [])]


def test_aligner_stops_when_delineation_states_repeat():
    """Aligner should stop when neighboring decisions form a cycle."""
    alignment = _get_alignment()
    delineation_queryer = Mock(spec=Queryer)
    delineation_queryer.prompt = _LOCALIZED_PROMPT

    def oscillate(test_case: DelineationTestCase) -> DelineationTestCase:
        """Move the second target left, then move it back right."""
        answer = {"output_one": "甲乙"}
        if not test_case.query.target_two:
            answer = {"output_one": "甲", "output_two": "乙"}
        return type(test_case).model_validate(
            {
                **test_case.model_dump(),
                "answer": answer,
            }
        )

    delineation_queryer.side_effect = oscillate
    aligner = TranscriptionAligner(
        delineation_queryer=delineation_queryer,
        punctuation_queryer=Mock(spec=Queryer),
    )

    with patch.object(aligner, "_punctuate") as punctuate:
        aligner.align(alignment.reference, alignment.transcription)

    assert delineation_queryer.call_count == 2
    punctuate.assert_called_once()
