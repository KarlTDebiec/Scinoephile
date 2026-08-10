#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for Cantonese transcription alignment scoring."""

from __future__ import annotations

from scinoephile.lang.yue.transcription_validation import (
    CantoneseTranscriptionAlignmentScorer,
)
from scinoephile.llms.transcription import (
    TranscriptionAlignmentScorer,
    TranscriptionCharacterRelationship,
)


def test_cantonese_alignment_scorer_adds_cantonese_equivalence():
    """Cantonese substitutions should be equivalent only in the Yue scorer."""
    generic_scorer = TranscriptionAlignmentScorer()
    cantonese_scorer = CantoneseTranscriptionAlignmentScorer()

    assert (
        generic_scorer.get_character_relationship("不", "唔")
        is TranscriptionCharacterRelationship.none
    )
    assert (
        cantonese_scorer.get_character_relationship("不", "唔")
        is TranscriptionCharacterRelationship.equivalent
    )


def test_cantonese_alignment_scorer_uses_jyutping():
    """Cantonese homophones should provide pronunciation-level support."""
    scorer = CantoneseTranscriptionAlignmentScorer()

    assert (
        scorer.get_character_relationship("道", "盜")
        is TranscriptionCharacterRelationship.pronunciation
    )
