#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Yue scoring of transcription alignment evidence."""

from __future__ import annotations

from scinoephile.lang.yue.character_features import (
    CharacterRelationship,
    get_character_relationship,
)
from scinoephile.llms.transcription import (
    TranscriptionAlignmentScorer,
    TranscriptionCharacterRelationship,
)

__all__ = ["YueTranscriptionAlignmentScorer"]


class YueTranscriptionAlignmentScorer(TranscriptionAlignmentScorer):
    """Score transcription alignment using Yue character relationships."""

    def get_character_relationship(
        self, one: str, two: str
    ) -> TranscriptionCharacterRelationship:
        """Classify Yue support between two characters.

        Arguments:
            one: first character
            two: second character
        Returns:
            relationship between the characters
        """
        relationship = get_character_relationship(one, two)
        if relationship is CharacterRelationship.EXACT:
            return TranscriptionCharacterRelationship.EXACT
        if relationship >= CharacterRelationship.EQUIVALENT:
            return TranscriptionCharacterRelationship.EQUIVALENT
        if relationship >= CharacterRelationship.SAME_JYUTPING_BASE:
            return TranscriptionCharacterRelationship.PRONUNCIATION
        return TranscriptionCharacterRelationship.NONE
