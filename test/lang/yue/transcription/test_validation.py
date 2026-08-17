#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Yue transcription alignment scoring."""

from __future__ import annotations

from scinoephile.lang.yue.transcription.validation import (
    YueTranscriptionAlignmentScorer,
)
from scinoephile.llms.transcription import (
    TranscriptionAlignmentScorer,
    TranscriptionCharacterRelationship,
)


def test_yue_alignment_scorer_adds_yue_equivalence():
    """Yue substitutions should be equivalent only in the Yue scorer."""
    generic_scorer = TranscriptionAlignmentScorer()
    yue_scorer = YueTranscriptionAlignmentScorer()

    assert (
        generic_scorer.get_character_relationship("不", "唔")
        is TranscriptionCharacterRelationship.none
    )
    assert (
        yue_scorer.get_character_relationship("不", "唔")
        is TranscriptionCharacterRelationship.equivalent
    )


def test_yue_alignment_scorer_uses_jyutping():
    """Yue homophones should provide pronunciation-level support."""
    scorer = YueTranscriptionAlignmentScorer()

    assert (
        scorer.get_character_relationship("道", "盜")
        is TranscriptionCharacterRelationship.pronunciation
    )


def test_yue_alignment_scorer_preserves_pronunciation_matches():
    """Pronunciation-equivalent orthography should preserve majority evidence."""
    validation = YueTranscriptionAlignmentScorer().score(("啊", "啊", "啊"), "呀")

    assert validation.majority_coverage == 1.0
    assert validation.preserves_required_majority(0.9)
